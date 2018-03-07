import miner as Gm
import refine
import pickle

if __name__ == "__main__":
    # Infer grammar
    traces = pickle.load(open( "traces.p", "rb" ))
    grammar = Gm.get_merged_grammar(traces)
    print()
    # Output it
    print("Merged grammar ->\n" + Gm.grammar_to_string(grammar))
    print()
    g = refine.filter_unused(refine.filter_redundant(grammar))
    print("Filtered grammar ->\n" + Gm.grammar_to_string(g))
