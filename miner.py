#!/usr/bin/env python3
# Mine a grammar from dynamic behavior
import pudb; brk = pudb.set_trace
import grammar as g

class V:
    def __init__(self, v):
        self._taint = v._taint
        self._rindex = {range(0, len(self._taint)): v}

    def __lt__(self, o): return str(self).__lt__(str(o))
    def __repr__(self): return 'V:%s' % self.value()

    def value(self):
        return ''.join([self._rindex[k]
            for k in sorted(self._rindex, key=lambda a: a.start)])


    def cur_taint(self):
        t = [-1] * len(self.taint)
        for k in sorted(self._rindex, key=lambda a: a.start):
            v = self._rindex[k]
            if hasattr(v, '_taint'): t[k.start:k.stop] = v._taint
        return t

    def _tinclude(self, o):
        return next((k for k in self._rindex if set(o._taint) <= set(k)), None)

    def _in_range(self, o):
        return self.taint[0] <= o._taint[0] and self.taint[-1] >= o._taint[-1]

    @property
    def taint(self): return self._taint

    def include(self, word):
        if not self._in_range(word): return None
        # When we paste the taints of new word in, (not replace)
        # then, does it get us more coverage? (i.e more -1s)
        cur_tsum = sum(i for i in self.cur_taint() if i < 0)
        t = self.taint[:]
        start_i,stop_i = t.index(word._taint[0]),t.index(word._taint[-1])
        t[start_i:stop_i+1] = [-1] * len(word)
        new_sum = sum(i for i in t if i < 0)
        if new_sum <= cur_tsum: return new_sum - cur_tsum
        return None

    def replace(self, o, repl):
        # we need to handle these
        # s = peek(1)
        # if s == 't': read_str('true')
        # or 
        # i = read_num(), point = read('.'), d = read_num()
        # number = i + point + d
        taintkey = self._tinclude(o)
        if not taintkey:
            # the complete taint range is not contained, but we are still
            # inclued in the original. It means that an inbetween variable has
            # obscured our inclusion.
            to_rem = []
            for k in sorted(self._rindex, key=lambda a: a.start):
                if o._taint[0] <= k.start <= o._taint[-1]:
                    assert o._taint[0] <= k.stop <= o._taint[-1]+1
                    to_rem.append(k)
            for k in to_rem: del self._rindex[k]
            self._rindex[range(o._taint[0], o._taint[-1]+1)] = repl
            return

        # get starting point.
        reprange = range(o._taint[0], o._taint[-1] + 1)
        my_str = self._rindex[taintkey]
        del self._rindex[taintkey]
        splitA = reprange.start - taintkey.start
        splitB = splitA + len(o)
        init_range = range(taintkey.start, reprange.start)
        mid_range = range(reprange.start, reprange.stop)
        end_range = range(reprange.stop, taintkey.stop)
        if init_range: self._rindex[init_range] = my_str[0:splitA]
        self._rindex[mid_range] = repl
        if end_range: self._rindex[end_range] = my_str[splitB:]

def nonterminal(var): return "$" + var.upper()

# Obtain a grammar for a specific input
def get_grammar(assignments):
    my_grammar = g.Grammar()
    # all values are tainted strings.
    for var, value in assignments.items():
        nt_var = nonterminal(var)
        append = False if my_grammar else True
        for _, repl_alternatives in my_grammar.items():
            # if value taint is a proper subset of repl taint
            res = [repl for repl in repl_alternatives if repl.include(value)]
            for repl in res: repl.replace(value, nt_var)
            append = True
        if append: my_grammar[nt_var] = {V(value)}
    return my_grammar

def merge_grammars(g1, g2):
    return g.Grammar({key: g1[key] | g2[key] for key in g1.keys() + g2.keys()})

# Get a grammar for multiple inputs
def infer_grammar(traces):
    merged_grammar = g.Grammar()
    for instr, defs in traces:
        grammar = get_grammar(defs)
        # print(repr(instr) + " ->\n" + str(grammar))
        merged_grammar = merge_grammars(merged_grammar, grammar)
    return merged_grammar

