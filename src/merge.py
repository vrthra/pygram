import json
import induce
import sys
import os
import collections

verbose = os.getenv('VERBOSE', '').strip()

def log(var):
    if verbose: print(var, file=sys.stderr)

if __name__ == "__main__":
    line = '_'* 80
    if sys.argv[1] == '-':
        count = 0
        with induce.grammar() as g:
            for sframe in sys.stdin:
                if not sframe: continue
                jframe = json.loads(sframe)
                if not g.handle_events(jframe):
                    count += 1
                    log("[%d]%s\n%s" % (count, line, g))
    else:
        data = induce.slurplstriparg()
        data_len = len(data)
        with induce.grammar() as g:
            for count, sframe in enumerate(data):
                if not sframe: continue
                jframe = json.loads(sframe)
                if not g.handle_events(jframe):
                    log("[%d%%]%s\n%s" % (count * 100.0/data_len, line, g))
