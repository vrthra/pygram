#!/usr/bin/env python3
# Grammar-based Fuzzing

# This program is copyright (c) 2017 Saarland University.
# Written by Andreas Zeller <zeller@cs.uni-saarland.de>.
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


import random
import re
import sys
import json

# We define a grammar as mappings of nonterminals into possible expansions.
# Possible expansions come as a list of alternatives
term_grammar = {
    "$START":
        ["$EXPR"],

    "$EXPR":
        ["$EXPR + $TERM", "$EXPR - $TERM", "$TERM"],

    "$TERM":
        ["$TERM * $FACTOR", "$TERM / $FACTOR", "$FACTOR"],

    "$FACTOR":
        ["+$FACTOR", "-$FACTOR", "($EXPR)", "$INTEGER", "$INTEGER.$INTEGER"],

    "$INTEGER":
        ["$INTEGER$DIGIT", "$DIGIT"],

    "$DIGIT":
        ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
}

html_grammar = {
    "$START":
        ["$DOCUMENT"],

    "$DOCUMENT":
        ["$DOCTYPE$HTML"],

    "$DOCTYPE":
        ['<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN"\n' + \
         '"http://www.w3.org/TR/html4/strict.dtd">\n'],

    "$HTML":
        ["<HTML>$HEAD$BODY</HTML>\n"],

    "$HEAD":
        ["<HEAD>$TITLE</HEAD>\n"],

    "$TITLE":
        ["<TITLE>A generated document</TITLE>\n"],

    "$BODY":
        ["<BODY>$DIVS</BODY>\n"],

    "$DIVS":
        ["$A_DIV", "$A_DIV\n$DIVS"],

    "$A_DIV":
        ["$A_HEADER\n$LIST"],

    "$A_HEADER":
        ["<H1>A header.</H1>", "<H1>Another header.</H1>"],

    "$LIST":
        ["<UL>$ITEMS</UL>", "<OL>$ITEMS</OL>"],

    "$ITEMS":
        ["$AN_ITEM", "$AN_ITEM$ITEMS"],

    "$AN_ITEM":
        ["<LI>$TEXT</LI>\n"],

    "$TEXT":
        ["An item", "Another item"]
}


# A regular expression matching the nonterminals used in this grammar
RE_NONTERMINAL = r'\$[a-zA-Z_]*'

# For debugging:
DEBUG = False
def log(s):
    if DEBUG:
        print(s() if callable(s) else s)

# We create a derivation tree with nodes in the form (SYMBOL, CHILDREN)
# where SYMBOL is either a nonterminal or terminal,
# and CHILDREN is
# - a list of children (for nonterminals)
# - an empty list for terminals
# - None for nonterminals that are yet to be expanded
# Example:
# ("$START", None) - the initial tree with just the root node
# ("$START", [("$EXPR", None)]) - expanded once into $START -> $EXPR
# ("$START", [("$EXPR", [("$EXPR", None]), (" + ", []]), ("$TERM", None])]) -
#     expanded into $START -> $EXPR -> $EXPR + $TERM

# Return an initialized tree
def init_tree(grammar, start_symbol = "$START"):
    return (start_symbol, None)

# Convert an expansion rule to children
def expansion_to_children(expansion):
    # print("Converting " + repr(expansion))

    # All symbols in the expansion rule
    symbols  = re.findall(RE_NONTERMINAL, expansion)
    # print(symbols)

    # Split the expansion rule by nonterminals,
    # giving us a list of only terminals
    children_without_symbols = re.split(RE_NONTERMINAL, expansion)
    # print(children_without_symbols)

    assert len(children_without_symbols) == len(symbols) + 1

    # Put it all back together
    children = []
    i = 0
    for c in children_without_symbols:
        if len(c) > 0:
            # Nonterminal
            children.append((c, []))
        if i < len(symbols):
            # Symbol
            children.append((symbols[i], None))
            i += 1

    # print("Converting " + repr(expansion) + " to " + repr(children))

    return children

# Expand a node
def expand_node(node, grammar, prefer_shortest_expansion):
    (symbol, children) = node
    # print("Expanding " + repr(symbol))
    assert children is None

    # Fetch the possible expansions from grammar...
    expansions = grammar[symbol]
    possible_children = []

    # ...as well as the shortest ones
    # TODO: A shorter "local" expansion does not imply we'll obtain a shorter
    # "global" expansion.  Maybe a lookahead with a certain depth?
    shortest_children = []
    shortest_children_len = None

    for expansion in expansions:
        # Convert into children
        possible_child = expansion_to_children(expansion)
        possible_children.append(possible_child)

        # Keep the list of shortest children
        if shortest_children_len is None or len(possible_child) < shortest_children_len:
            shortest_children     = [possible_child]
            shortest_children_len = len(possible_child)
        elif len(possible_child) == shortest_children_len:
            shortest_children.append(possible_child)

    # Pick a child randomly
    if prefer_shortest_expansion:
        children = random.choice(shortest_children)
    else:
        # TODO: Consider preferring children not expanded yet,
        # and other forms of grammar coverage (or code coverage)
        children = random.choice(possible_children)

    # Return with a new list
    return (symbol, children)

# Count possible expansions -
# that is, the number of (SYMBOL, None) nodes in the tree
def possible_expansions(tree):
    (symbol, children) = tree
    if children is None:
        return 1

    number_of_expansions = sum(possible_expansions(c) for c in children)
    return number_of_expansions

# Expand the tree once
def expand_tree_once(tree, grammar, prefer_shortest_expansion):
    (symbol, children) = tree
    if children is None:
        # Expand this node
        return expand_node(tree, grammar, prefer_shortest_expansion)

    # print("Expanding tree " + repr(tree))

    # Find all children with possible expansions
    expandable_children = [i for (i, c) in enumerate(children) if possible_expansions(c)]

    # Select a random child
    # TODO: Various heuristics for choosing a child here,
    # e.g. grammar or code coverage
    child_to_be_expanded = random.choice(expandable_children)

    # Expand it
    new_child = expand_tree_once(children[child_to_be_expanded], grammar, prefer_shortest_expansion)

    new_children = (children[:child_to_be_expanded] +
                    [new_child] +
                    children[child_to_be_expanded + 1:])

    new_tree = (symbol, new_children)

    # print("Expanding tree " + repr(tree) + " into " + repr(new_tree))

    return new_tree

# Keep on applying productions
# TODO: We limit production by the number of symbols;
# alternate limits (e.g. length of overall string) are possible too
# TODO: One may also want a _minimum_ length or number of symbols
def expand_tree(tree, grammar, max_symbols):
    # Stage 1: Expand until we reach the max number of symbols
    log("Expanding")
    while 0 < possible_expansions(tree) < max_symbols:
        tree = expand_tree_once(tree, grammar, False)
        log(lambda: all_terminals(tree))

    # Stage 2: Keep on expanding, but now focus on the shortest expansions
    log("Closing")
    while possible_expansions(tree) > 0:
        tree = expand_tree_once(tree, grammar, True)
        log(lambda: all_terminals(tree))

    return tree

# The tree as a string
def all_terminals(tree):
    (symbol, children) = tree
    if children is None:
        # This is a nonterminal symbol not expanded yet
        return symbol

    if len(children) == 0:
        # This is a terminal symbol
        return symbol

    # This is an expanded symbol:
    # Concatenate all terminal symbols from all children
    return ''.join([all_terminals(c) for c in children])

# All together
def produce(grammar, max_symbols = 10):
    # Create an initial derivation tree
    tree = init_tree(grammar)
    # print(tree)

    # Expand all nonterminals
    tree = expand_tree(tree, grammar, max_symbols)
    # print(tree)

    # Return the string
    return all_terminals(tree)

if __name__ == "__main__":
    # The grammar to use
    with open(sys.argv[1], 'r') as input:
        grammar = json.load(input)
        #for obj in grammar: print(obj)

        for i in range(1, 20):
            print(produce(grammar))
