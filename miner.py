#!/usr/bin/env python3
# Mine a grammar from dynamic behavior

from tstr import get_t
import pudb
brk = pudb.set_trace

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
        res = ''.join([self._index_map[k] for k in
            sorted(self._index_map.keys(), key=lambda a: a.start)])
        return res

    def __str__(self):
        res = ''.join([self._index_map[k] for k in
            sorted(self._index_map.keys(), key=lambda a: a.start)])
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

# Convert a variable name into a grammar nonterminal
def nonterminal(var):
    return "$" + var.upper()

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
def infer_grammar(traces):
    merged_grammar = {}
    for instr, defs in traces:
        grammar = get_grammar(defs)
        print(repr(instr) + " ->\n" + grammar_to_string(grammar))
        merged_grammar = merge_grammars(merged_grammar, grammar)
    return merged_grammar

