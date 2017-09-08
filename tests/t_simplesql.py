import simplesql
import induce, helpers

with induce.grammar() as g:
    for l in helpers.slurplstriparg():
       with induce.Tracer(l.strip(), g):
          simplesql.simpleSQL.parseString(l)
