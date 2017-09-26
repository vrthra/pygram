import simplearith
import induce, helpers

with induce.grammar() as g:
  for t in helpers.slurplstriparg():
    with induce.Tracer(t, g):
        simplearith.expr.parseString(t)

