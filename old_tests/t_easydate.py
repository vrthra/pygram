import easy_date
import helpers,induce
with induce.grammar() as g:
   lines = helpers.slurplstriparg()
   for l in lines:
      dat, fmt = l.split('|')
      with induce.Tracer(dat, g):
         dt = easy_date.convert_from_string(dat, fmt, '%Y-%m-%d')
