#!/usr/bin/env python

import json
import induce
import sys

with induce.grammar() as g:
    for sframe in sys.stdin:
        if len(sframe.strip()) == 0: continue # end of a complete activation
        jframe = json.loads(sframe)
        g.update(jframe)
        print g
        print "_" * 80
