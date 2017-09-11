#!/usr/bin/env python
# Mine a grammar from dynamic behavior

import sys
import random

from urlparse import urlparse

def slurp(src):
    with open(src) as x: return x.readlines()

# Convert a variable name into a grammar nonterminal
def nonterminal(var):
    return "$" + var.upper()
 
# Pretty-print a grammar   
def grammar_to_string(grammar):
    s = ""
    for key in grammar.keys():
        s = s + key + " ::= "
        s = s + " | ".join(grammar[key])
        s = s + "\n"
    return s

# Obtain a grammar for a specific input
def get_grammar(the_input):
    # Here's our initial grammar
    grammar = {"$START": [the_input]}

    # We obtain a mapping of variables to values

    # We store individual variable/value pairs here
    the_values = {}

    # We record all string variables and values occurring during execution
    def traceit(frame, event, arg):
        variables = frame.f_locals.keys()

        for var in variables:
            value = frame.f_locals[var]
            # print(var, value)

            # Save all non-trivial string values that also occur in the input
            if type(value) == type('') and len(value) >= 2 and value in the_input:
                the_values[var] = value

        return traceit


    
    sys.settrace(traceit)
    o = urlparse(the_input)
    sys.settrace(None)

    # Now for each (VAR, VALUE) found:
    # 1. We search for occurrences of VALUE in the grammar
    # 2. We replace them by $VAR
    # 3. We add a new rule $VAR -> VALUE to the grammar
    while True:
        new_rules = []
        for var in the_values.keys():
            value = the_values[var]
            for key in grammar.keys():
                repl_alternatives = grammar[key]
                for j in range(0, len(repl_alternatives)):
                    repl = repl_alternatives[j]
                    if value in repl:
                        # Found variable value in some grammar nonterminal
                    
                        # Replace value by nonterminal name
                        alt_key = nonterminal(var)
                        repl_alternatives[j] = repl.replace(value, alt_key)
                        new_rules = new_rules + [(var, alt_key, value)]
        
        if len(new_rules) == 0:
            break # Nothing to expand anymore
            
        for (var, alt_key, value) in new_rules:
            # Add new rule to grammar
            grammar[alt_key] = [value]

            # Do not expand this again
            del the_values[var]
                        
    return grammar

# Merge two grammars G1 and G2
def merge_grammars(g1, g2):
    merged_grammar = g1
    for key2 in g2.keys():
        repl2 = g2[key2]
        key_found = False
        for key1 in g1.keys():
            repl1 = g1[key1]
            for repl in repl2:
                if key1 == key2:
                    key_found = True
                    if repl not in repl1:
                        # Extend existing rule
                        merged_grammar[key1] = repl1 + [repl]
                        
        if not key_found:
            # Add new rule
            merged_grammar[key2] = repl2
    return merged_grammar

# Get a grammar for multiple inputs
def get_merged_grammar(inputs):
    merged_grammar = None
    for input in inputs:
        grammar = get_grammar(input)
        print( "%s -> %s" % (repr(input), grammar_to_string(grammar)))
        if merged_grammar is None:
            merged_grammar = grammar
        else:
            merged_grammar = merge_grammars(merged_grammar, grammar)

    return merged_grammar
    
def apply_rule(term, rule):
    (old, new) = rule
    # We replace the first occurrence; 
    # this could also be some random occurrence
    return term.replace(old, new, 1)

if __name__ == "__main__":
    lines = [l.strip() for l in slurp(sys.argv[1])]
    # Infer grammar
    grammar = get_merged_grammar(lines)

    # Output it
    print("Merged grammar -> %s" % grammar_to_string(grammar))
