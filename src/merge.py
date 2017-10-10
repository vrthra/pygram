import json
import induce
import sys
import os
import collections
from contextlib import contextmanager

verbose = os.getenv('VERBOSE', '').strip()

@contextmanager
def grammar():
    refiner = induce.Refiner()
    mygrammar = induce.Grammar(refiner)
    yield mygrammar
    lines = "_" * 80
    print(("%s\n%s\n%s" % (lines, refiner, lines)))

def log(var):
    if verbose: print(var, file=sys.stderr)

if __name__ == "__main__":
    line = '_'* 80
    if sys.argv[1] == '-':
        count = 0
        with grammar() as g:
            for sframe in sys.stdin:
                if not sframe: continue
                jframe = json.loads(sframe)
                if not g.handle_events(jframe):
                    count += 1
                    log("[%d]%s\n%s" % (count, line, g))
    else:
        data = induce.slurplstriparg()
        data_len = len(data)
        with grammar() as g:
            for count, sframe in enumerate(data):
                if not sframe: continue
                jframe = json.loads(sframe)
                if not g.handle_events(jframe):
                    log("[%d%%]%s\n%s" % (count * 100.0/data_len, line, g))
