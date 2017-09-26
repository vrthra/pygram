import arrow
import helpers,induce
with induce.grammar() as g:
   lines = helpers.slurplstriparg()
   for l in lines:
      with induce.Tracer(l, g):
         dt = arrow.get(l)
