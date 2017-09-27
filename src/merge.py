import json
import induce
import sys
import collections

data = induce.slurplstriparg()
l = len(data)
with induce.grammar() as g:
    for count, sframe in enumerate(data):
        if not sframe: continue
        jframe = json.loads(sframe)
        if not jframe:
            g.reset()
        else:
            # end of a complete activation
            g.update(jframe)
