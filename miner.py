#!/usr/bin/env python3
# Mine a grammar from dynamic behavior
import pudb; brk = pudb.set_trace
import grammar as g

class V:
    def __init__(self, v):
        self._taint = v._taint
        self._rindex = {tainted_range(self._taint): v}

    def ranges(self): return sorted(self._rindex, key=lambda a: a.start)
    def __lt__(self, o): return str(self).__lt__(str(o))
    def __repr__(self): return 'V:%s' % self.value()
    def value(self): return ''.join(self._rindex[k] for k in self.ranges())


    def cur_taint(self):
        t = [-1] * len(self.taint)
        for k in self.ranges():
            v = self._rindex[k]
            if hasattr(v, '_taint'): t[k.start:k.stop] = v._taint
        return t

    def _tinclude(self, o):
        return next((k for k in self._rindex if set(o._taint) <= set(k)), None)

    def _encloses(self, o):
        return self.taint[0] <= o._taint[0] and self.taint[-1] >= o._taint[-1]

    @property
    def taint(self): return self._taint

    def keys_enclosed_by(self, largerange):
        l = [k for k in self.ranges() if k.start in largerange]
        assert all(k.stop - 1 in largerange for k in l)
        return l

    def include(self, word):
        if not self._encloses(word): return None
        # When we paste the taints of new word in, (not replace)
        # then, does it get us more coverage? (i.e more -1s)
        cur_tsum = sum(i for i in self.cur_taint() if i < 0)
        ts = self.taint[:] # the original taint
        start_i, stop_i = ts.index(word._taint[0]), ts.index(word._taint[-1])
        ts[start_i:stop_i+1] = [-1] * len(word)
        new_sum = sum(i for i in ts if i < 0)
        if new_sum <= cur_tsum: return new_sum - cur_tsum
        return None

    def replace(self, o, repl):
        # we need to handle these
        # s = peek(1)
        # if s == 't': read_str('true')
        # or
        # i = read_num(), point = read('.'), d = read_num()
        # number = i + point + d
        trange = tainted_range(o._taint)
        keytaint = self._tinclude(o)
        if not keytaint:
            # the complete taint range is not contained, but we are still
            # inclued in the original. It means that an inbetween variable has
            # obscured our inclusion.
            to_rem = self.keys_enclosed_by(trange)
            for k in to_rem: del self._rindex[k]
            self._rindex[trange] = repl
        else:
            # get starting point.
            my_str = self._rindex[keytaint]
            del self._rindex[keytaint]
            splitA = trange.start - keytaint.start
            init_range = range(keytaint.start, trange.start)
            mid_range = range(trange.start, trange.stop)
            end_range = range(trange.stop, keytaint.stop)
            if init_range: self._rindex[init_range] = my_str[0:splitA]
            self._rindex[mid_range] = repl
            if end_range: self._rindex[end_range] = my_str[splitA + len(o):]

def nonterminal(var): return "$" + var.upper()
def tainted_range(tarr): return range(tarr[0], tarr[-1]+1)

# Obtain a grammar for a specific input
def get_grammar(assignments):
    my_grammar = g.Grammar()
    # all values are tainted strings.
    for var, value in assignments.items():
        append = False if my_grammar else True
        for _, repl_alternatives in my_grammar.items():
            res = [repl for repl in repl_alternatives if repl.include(value)]
            for repl in res: repl.replace(value, var)
            append = True
        if append: my_grammar[var] = {V(value)}
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

