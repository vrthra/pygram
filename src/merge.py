import json
import induce
import sys
import collections

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
                    print("[%d]%s\n%s" % (count, line, g), file=sys.stderr)
    else:
        data = induce.slurplstriparg()
        data_len = len(data)
        with induce.grammar() as g:
            for count, sframe in enumerate(data):
                if not sframe: continue
                jframe = json.loads(sframe)
                if not g.handle_events(jframe):
                    print("[%d%%]%s\n%s" % (count * 100.0/data_len, line, g), file=sys.stderr)
