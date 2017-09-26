import json
import induce
import sys
import collections

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
        myframe = collections.OrderedDict()
        for k in sorted(jframe.keys()): myframe[k] = jframe[k]
        g.update(myframe)
