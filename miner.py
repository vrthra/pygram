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

# REFACTOR:
# * We need to rethink how grammar is derived for loopy subjects.
#   Rather than merge the grammar at the end of execution, we need to
#   treat each iteration of each loop as a mechanism to produce a simple
#   gramamr, then merge these grammars together at one go.
# * Join the line number to the variable name so that a reassignment is
#   treated as a new variable (but not for a new iteration).
# * We can detect a new loop by looking for reasignment on the same
#   variable with same line number.
#
# * Split the string objects rather than replace with nt_var
# * When looking for old_taints, ensure that the newly replaced stuff
#   is actually better than the old vars
# * Take a leaf out of the regex paper, and allow single character values
#   with no replacements to be embedded directly rather than as a non-terminal.

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

from tstr import get_t
import pudb
brk = pudb.set_trace

Current = None
Fuzz = False

# Convert a variable name into a grammar nonterminal
def nonterminal(var):
    return "$" + var.upper()

def grammar_to_string(rules):
    def djs_to_string(djs):
        return "\n\t| ".join([i.value().replace('\n', '\n|\t') for i in sorted(djs)])
    def fixline(key, rules):
        fmt = "%s ::= %s" if len(rules) == 1 else "%s ::=\n\t| %s"
        return fmt % (key, djs_to_string(rules))
    return "\n".join([fixline(key, rules[key]) for key in rules.keys()])

class V:
    def __init__(self, v):
        self.v = v
        self._taint = get_t(v)._taint
        self._index_map = {}
        self._index_map[range(0, len(self._taint))] = get_t(v)
        self._old_taints = []

    def __lt__(self, o):
        return str(self).__lt__(str(o))

    def value(self):
        res = ''.join([self._index_map[k] for k in sorted(self._index_map.keys(), key=lambda a: a.start)])
        return res

    def __str__(self):
        res = ''.join([self._index_map[k] for k in sorted(self._index_map.keys(), key=lambda a: a.start)])
        return res

    def cur_taint(self):
        t = [-1] * len(get_t(self.v))
        for k in sorted(self._index_map.keys(), key=lambda a: a.start):
            v = get_t(self._index_map[k])
            if v:
                t[k.start:k.stop] = v._taint
        return t

    def _tinclude(self, o):
        for k in self._index_map:
            if set(o._taint) <= set(k):
                return k, range(o._taint[0], o._taint[-1]+1)
        return None

    def _in_range(self, o):
        return self._taint[0] <= o._taint[0] and self.taint[-1] >= o._taint[-1]

    @property
    def taint(self):
        return self._taint

    def include(self, word):
        gword = get_t(word)
        if not gword: return None
        if self._in_range(gword):
            # When we paste the taints of new word in, (not replace)
            # then, does it get us more coverage? (i.e more -1s)
            cur_tsum = sum(i for i in self.cur_taint() if i < 0)
            t = self._taint[:]
            start_i = t.index(gword._taint[0])
            stop_i = t.index(gword._taint[-1])
            t[start_i:stop_i+1] = [-1] * len(gword)
            new_sum = sum([i for i in t if i < 0])
            if new_sum <= cur_tsum:
                return new_sum - cur_tsum
            return None
        return None

    def replace(self, to_replace, orig, repl):
        taintft = self._tinclude(get_t(orig))
        if not taintft:
            # remove every range that is completely contained
            # assert that no overlapping range found.
            to_rem = []
            for k in sorted(self._index_map.keys(), key=lambda a: a.start):
                o = get_t(orig)
                if o._taint[0] <= k.start <= o._taint[-1]:
                    assert o._taint[0] <= k.stop <= o._taint[-1]+1
                    to_rem.append(k)
            for k in to_rem:
                del self._index_map[k]
            self._index_map[range(o._taint[0], o._taint[-1]+1)] = repl
            return

        sorig = get_t(orig)
        # get starting point.
        taintkey, reprange = taintft
        my_str = self._index_map[taintkey]
        del self._index_map[taintkey]
        self._old_taints.append({taintkey: my_str})
        # insert the fraction between taintkey and frm
        # which corresponds to my_str
        # my_str[0] = taintkey.start
        x = (reprange.start - taintkey.start)
        if taintkey.start < reprange.start:
            self._index_map[range(taintkey.start, reprange.start)] = my_str[0:x]
        self._index_map[range(reprange.start, reprange.stop)] = repl
        if taintkey.stop > reprange.stop:
            self._index_map[range(reprange.stop, taintkey.stop)] = my_str[x + len(sorig):]


# Obtain a grammar for a specific input
def get_grammar(assignments):
    # For each (VAR, VALUE) found:
    # 1. We search for occurrences of VALUE in the grammar
    # 2. We replace them by $VAR
    # 3. We add a new rule $VAR -> VALUE to the grammar
    i = 0
    my_grammar = {}
    for var, value in assignments.items():
        i += 1
        nt_var = nonterminal(var)
        append = False
        for key, repl_alternatives in my_grammar.items():
            i += 1
            alt = set()
            # each repl is a dict
            for repl in repl_alternatives:
                i += 1
                if get_t(value):
                    # if value taint is a proper subset of repl taint
                    r = repl.include(value)
                    if r:
                        repl.replace(r, value, nt_var)
                        append = True
                elif type(value) is str and value in repl.v:
                    assert False
                alt.add(repl)
            my_grammar[key] = alt
        if append or not my_grammar:
            my_grammar[nt_var] = {V(value)}
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

