#!/usr/bin/env python3
# Mine a grammar from dynamic behavior

import pudb
import tstr
brk = pudb.set_trace

class V:
    def __init__(self, v):
        self.v = v
        self._taint = v._taint
        self._index_map = {range(0, len(self._taint)): v}

    def __lt__(self, o): return str(self).__lt__(str(o))

    def value(self):
        return ''.join([self._index_map[k] for k in
            sorted(self._index_map.keys(), key=lambda a: a.start)])

    def __repr__(self): return 'V:%s' % self.value()

    def cur_taint(self):
        t = [-1] * len(self.v)
        for k in sorted(self._index_map.keys(), key=lambda a: a.start):
            v = self._index_map[k]
            if type(v) is tstr.tstr:
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
    def taint(self): return self._taint

    def include(self, word):
        gword = word
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

    def replace(self, orig, repl):
        taintft = self._tinclude(orig)
        if not taintft:
            # the complete taint range is not contained, but we are still
            # inclued in the original. It means that an inbetween variable has
            # obscured our inclusion.
            to_rem = []
            for k in sorted(self._index_map.keys(), key=lambda a: a.start):
                o = orig
                if o._taint[0] <= k.start <= o._taint[-1]:
                    assert o._taint[0] <= k.stop <= o._taint[-1]+1
                    to_rem.append(k)
            for k in to_rem:
                del self._index_map[k]
            self._index_map[range(o._taint[0], o._taint[-1]+1)] = repl
            return

        sorig = orig
        # get starting point.
        taintkey, reprange = taintft
        my_str = self._index_map[taintkey]
        del self._index_map[taintkey]
        # insert the fraction between taintkey and frm
        # which corresponds to my_str
        # my_str[0] = taintkey.start
        x = (reprange.start - taintkey.start)
        init_range = range(taintkey.start, reprange.start)
        mid_range = range(reprange.start, reprange.stop)
        end_range = range(reprange.stop, taintkey.stop)
        if init_range: self._index_map[init_range] = my_str[0:x]
        self._index_map[mid_range] = repl
        if end_range: self._index_map[end_range] = my_str[x + len(sorig):]

# Convert a variable name into a grammar nonterminal
def nonterminal(var): return "$" + var.upper()

def grammar_to_string(rules):
    def djs_to_string(djs):
        return "\n\t| ".join([i.value().replace('\n', '\n|\t')
            for i in sorted(djs)])
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
    # all values are tainted strings.
    for var, value in assignments.items():
        nt_var = nonterminal(var)
        append = False if my_grammar else True
        for key, repl_alternatives in my_grammar.items():
            # if value taint is a proper subset of repl taint
            res = [repl for repl in repl_alternatives if repl.include(value)]
            for repl in res:
                repl.replace(value, nt_var)
                append = True
        if append: my_grammar[nt_var] = {V(value)}
    return my_grammar

# Merge two grammars G1 and G2
def merge_grammars(g1, g2):
    return {key: g1.get(key, set()) | g2.get(key, set())
            for key in list(g1.keys()) + list(g2.keys())}

# Get a grammar for multiple inputs
def infer_grammar(traces):
    merged_grammar = {}
    for instr, defs in traces:
        grammar = get_grammar(defs)
        # print(repr(instr) + " ->\n" + grammar_to_string(grammar))
        merged_grammar = merge_grammars(merged_grammar, grammar)
    return merged_grammar

