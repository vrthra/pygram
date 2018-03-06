import microjson
import tstr
import sys
import miner as Gm

INPUTS = [
   # '1',
   # '2',
   # '3',
   # 'true',
   # 'false',
   # 'null',
   '"hello"',
   # '{"hello":"world"}',
   # '[1, 2, 3]',
]

if __name__ == "__main__":
    # Infer grammar
    traces = []
    for _i in INPUTS:
        i = tstr.tstr(_i)
        Current = i
        Gm.Vars.init(i)
        oldtrace = sys.gettrace()
        sys.settrace(Gm.traceit)
        o = microjson.from_json(i)
        sys.settrace(oldtrace)
        traces.append((i, Gm.Vars.defs))
    grammar = Gm.get_merged_grammar(traces)
    print()
    # Output it
    print("Merged grammar ->\n" + Gm.grammar_to_string(grammar))
    print()
    g = Gm.filter_redundant(grammar)
    print("Filtered grammar ->\n" + Gm.grammar_to_string(Gm.filter_unused(g)))
