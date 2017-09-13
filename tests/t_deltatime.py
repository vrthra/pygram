from datetime import datetime
import deltatime
import induce, helpers

# test grammar
tests = helpers.slurplstriparg()
with induce.grammar() as g:
  print("(relative to %s)" % datetime.now())
  for t in tests:
    with induce.Tracer(t, g):
        print deltatime.nlTimeExpression.parseString(t)
