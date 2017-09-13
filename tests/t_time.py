import time
import helpers, induce

with induce.grammar() as g:
    for l in helpers.slurplstriparg():
       dat, fmt = l.split('|')
       with induce.Tracer(l, g):
          time.strptime(dat, fmt)
