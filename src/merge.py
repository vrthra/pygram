#!/usr/bin/env python

import json
import sys
import induce

with induce.grammar() as g:
    for sframe in induce.slurplstriparg():
        jframe = json.loads(sframe)
        g.update(jframe)
