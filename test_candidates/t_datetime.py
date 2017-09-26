from datetime import datetime
import helpers, induce

with induce.grammar() as g:
    for l in helpers.slurplstriparg():
       dat, fmt = l.split('|')
       with induce.Tracer(l, g):
          datetime.strptime(dat, fmt)
