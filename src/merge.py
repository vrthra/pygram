import json
import induce
import sys

data = induce.slurplstriparg()
l = len(data)
with induce.grammar() as g:
    for count, sframe in enumerate(data):
        # print("%s/%s" % (count, l),file=sys.stderr)
        sys.stderr.flush()
        if len(sframe.strip()) == 0:
            g.reset()
            continue # end of a complete activation
        jframe = json.loads(sframe)
        g.update(jframe)
