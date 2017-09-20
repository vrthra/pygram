#!/usr/bin/env python

import json
import induce

with induce.grammar() as g:
    for sframe in induce.slurplstriparg():
        if len(sframe.strip()) == 0:
            g.reset()
            continue # end of a complete activation
        jframe = json.loads(sframe)
        g.update(jframe)
