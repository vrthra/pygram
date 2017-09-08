from urlparse import urlparse
import helpers, induce

with induce.grammar() as g:
    for l in helpers.slurplstriparg():
       with induce.Tracer(l, g):
          urlparse(l)
