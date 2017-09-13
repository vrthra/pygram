from dateutil import parser
import helpers,induce
with induce.grammar() as g:
   lines = helpers.slurplstriparg()
   for l in lines:
      dat, fmt = l.split('|')
      with induce.Tracer(dat, g):
         dt = parser.parse(dat)
