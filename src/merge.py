#!/usr/bin/env python

import json
import induce

with induce.grammar() as g:
    for sframe in induce.slurplarg():
        if len(sframe.strip()) == 0: continue # end of a complete activation
        jframe = json.loads(sframe)
        g.update(jframe)
