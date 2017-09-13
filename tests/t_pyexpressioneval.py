from py_expression_eval import Parser

import induce, helpers

with induce.grammar() as g:
    lines = helpers.slurplstriparg()
    parser = Parser()
    for l in lines:
       with induce.Tracer(l, g):
          parser.parse(l)
