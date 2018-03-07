#!/usr/bin/env python3
import microjson
import tstr
import sys
import mtrace
import pickle

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
        mtrace.Vars.init(i)
        oldtrace = sys.gettrace()
        sys.settrace(mtrace.traceit)
        o = microjson.from_json(i)
        sys.settrace(oldtrace)
        traces.append((i, mtrace.Vars.defs))
    pickle.dump(traces, open( ".traces.p", "wb" ) )
