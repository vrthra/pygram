#!/usr/bin/env python3
import miner
import grammar as g
import refine
import pickle

if __name__ == "__main__":
    # Infer grammar
    traces = pickle.load(open( "traces.p", "rb" ))
    grammar = miner.infer_grammar(traces)
    print()
    # Output it
    print("Merged grammar ->\n" + str(grammar))
    print()
    grammar = refine.filter_unused(refine.filter_redundant(grammar))
    print("Filtered grammar ->\n" + str(g.Grammar(grammar)))
