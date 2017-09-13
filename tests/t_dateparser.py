import dateparser
import helpers,induce
with induce.grammar() as g:
   lines = helpers.slurplstriparg()
   for l in lines:
      print l
      with induce.Tracer(l, g):
         dt = dateparser.parse(l)
