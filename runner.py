import microjson
import tstr
import sys
import miner as Gm
import mtrace
import refine

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
        mtrace.Vars.init(i)
        oldtrace = sys.gettrace()
        sys.settrace(mtrace.traceit)
        o = microjson.from_json(i)
        sys.settrace(oldtrace)
        traces.append((i, mtrace.Vars.defs))
    grammar = Gm.get_merged_grammar(traces)
    print()
    # Output it
    print("Merged grammar ->\n" + Gm.grammar_to_string(grammar))
    print()
    g = refine.filter_unused(refine.filter_redundant(grammar))
    print("Filtered grammar ->\n" + Gm.grammar_to_string(g))
