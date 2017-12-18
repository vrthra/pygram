#!/usr/bin/env python3
# Mine a grammar from dynamic behavior

# This program is copyright (c) 2017 Saarland University.
# Written by Andreas Zeller <zeller@cs.uni-saarland.de>.
# Updated by Rahul Gopinath <rahul.gopinath@uni-saarland.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


# Changes:
# - Ordered addition of new variables as new variables are defined
#   (and slightly improved performance as a result)
# - A variable is only checked for inclusion on the current parameters
#   of the function.
# - Qualified (class:fn) names to avoid conflicts with similar variable
#   names in subroutines
# - Simplified grammar merge
# - Use string representation of objects to include more names in grammar
#
# TODO:
# * Add string globals to the string parameters and variables
#   being considered for rule replacements.
# * Expand nested objects and include the string variables within
#   them when doing rule replacements.
# * Currently the program does not manage what happens when the
#   same variable is reassigned -- such as during a loop. Fix this
#   so that reassignments are distinguished by a unique id.
# * Fix what happens when the same function is called repeatedly
#   from different parts. (Parameters, and variables)
# * When applying replace a variable value with the non-terminal
#   variable name, ensure that the replacement is done only on the
#   variables that are visible to the current variable.
# * Use simple taint-tracing or dataflow analysis to restrict the
#   number of rules in consideration when trying to do the
#   non-terminal replacement.
# * Use leave-n-out strategy to get the best non-terminal
#   replacements by avoiding spurious non-terminal inclusions.
# * When multiple matches are found for a variable value inside
#   a rule, include all combinations of the variable replacements
#   as rule choices.
# * Figure out better grammar compaction heuristics
# * Add a fuzzing step to test each individual choice in the rules
#   i.e. take a single input and the grammar derived from it, then
#   fuzz the input by using only a single choice and verify that
#   the choice is actually correct.

import sys
import random
import taint

from urllib.parse import urlparse

INPUTS = [
    'http://www.st.cs.uni-saarland.de/zeller#ref',
    'https://www.cispa.saarland:80/bar',
    'http://foo@google.com:8080/bar?q=r#ref2',
]

# We store individual variable/value pairs here
class Vars:
    defs = None

    def init(i):
        Vars.defs = {'START':i}

    def varname(var, frame):
        return var
        # class_name = frame.f_code.co_name
        # if frame.f_code.co_name == '__new__':
        #   class_name = frame.f_locals[frame.f_code.co_varnames[0]].__name__
        # return "%s:%s" % (class_name, var) # (frame.f_code.co_name, frame.f_lineno, var)

    def update_vars(var, value, frame):
        if not isinstance(value, str): return
        sval = value
        if len(sval) >= 2 and InputStack.has(sval):
           qual_var = Vars.varname(var, frame)
           if not Vars.defs.get(qual_var):
               Vars.defs[qual_var] = sval

def tainted(v):
    return isinstance(v, taint.tstr)


class InputStack:
    # The current input string
    inputs = []

    def has(val):
        return tainted(val) and any(val in var for var in InputStack.inputs[-1].values())

    def push(inputs):
        if InputStack.inputs:
            my_inputs = {k:v for k,v in inputs.items() if InputStack.has(v)}
            InputStack.inputs.append(my_inputs)
        else:
            my_inputs = {k:taint.tstr(v) for k,v in inputs.items() if isinstance(v, str)}
            InputStack.inputs.append(my_inputs)

    def pop():
        return InputStack.inputs.pop()

# We record all string variables and values occurring during execution
def traceit(frame, event, arg):
    if event == 'call':
        param_names = [frame.f_code.co_varnames[i]
                       for i in range(frame.f_code.co_argcount)]
        my_parameters = {k: v for k, v in frame.f_locals.items()
                         if k in param_names}
        InputStack.push(my_parameters)

        for var, value in my_parameters.items():
            Vars.update_vars(var, value, frame)
        return traceit

    if event == 'return':
        InputStack.pop()
        return traceit

    if event == 'exception':
        return traceit

    variables = frame.f_locals
    for var, value in variables.items():
        Vars.update_vars(var, value, frame)

    return traceit

# Convert a variable name into a grammar nonterminal
def nonterminal(var):
    return "$" + var.upper()

def grammar_to_string(rules):
    def djs_to_string(djs):
        return "\n\t| ".join([i.replace('\n', '\n|\t') for i in sorted(djs)])
    def fixline(key, rules):
        fmt = "%s ::= %s" if len(rules) == 1 else "%s ::=\n\t| %s"
        return fmt % (key, djs_to_string(rules))
    return "\n".join([fixline(key, rules[key]) for key in rules.keys()])

# Obtain a grammar for a specific input
def get_grammar(assignments):
    # For each (VAR, VALUE) found:
    # 1. We search for occurrences of VALUE in the grammar
    # 2. We replace them by $VAR
    # 3. We add a new rule $VAR -> VALUE to the grammar
    my_grammar = {}
    for var, value in assignments.items():
        nt_var = nonterminal(var)
        append = False
        for key, repl_alternatives in my_grammar.items():
            alt = set()
            for repl in repl_alternatives:
                if value in repl:
                   repl = repl.replace(value, nt_var)
                   append = True
                alt.add(repl)
            my_grammar[key] = alt
        if append or not my_grammar:
            my_grammar[nt_var] = {value}
    return my_grammar

# Merge two grammars G1 and G2
def merge_grammars(g1, g2):
    return {key: g1.get(key, set()) | g2.get(key, set())
            for key in list(g1.keys()) + list(g2.keys())}

# Get a grammar for multiple inputs
def get_merged_grammar(traces):
    merged_grammar = {}
    for instr, defs in traces:
        grammar = get_grammar(defs)
        print(repr(instr) + " ->\n" + grammar_to_string(grammar))
        merged_grammar = merge_grammars(merged_grammar, grammar)
    return merged_grammar

def apply_rule(term, rule):
    (old, new) = rule
    # We replace the first occurrence;
    # this could also be some random occurrence
    return term.replace(old, new, 1)

MAX_SYMBOLS = 5
MAX_TRIES = 500

def produce(grammar):
    term = "$START"
    tries = 0

    while term.count('$') > 0:
        # All rules have the same chance;
        # this could also be weighted
        key = random.choice(list(grammar.keys()))
        repl = random.choice(list(grammar[key]))
        new_term = apply_rule(term, (key, repl))
        if new_term != term and new_term.count('$') < MAX_SYMBOLS:
            term = new_term
            # print(term)
            tries = 0
        else:
            tries += 1
            if tries >= MAX_TRIES:
                assert False, "Cannot expand " + term

    return term

if __name__ == "__main__":
    # Infer grammar
    traces = []
    for i in INPUTS:
        Vars.init(i)
        oldtrace = sys.gettrace()
        sys.settrace(traceit)
        o = urlparse(taint.tstr(i).taint())
        sys.settrace(oldtrace)
        traces.append((i, Vars.defs))

    grammar = get_merged_grammar(traces)
    print()
    # Output it
    print("Merged grammar ->\n" + grammar_to_string(grammar))

    # Fuzz a little
    print("Fuzzing ->")
    for i in range(1, 10):
        print(produce(grammar))
