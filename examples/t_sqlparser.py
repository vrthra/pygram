import sqlparse
import induce

for l in induce.slurplstriparg():
   with induce.Tracer(l):
      sqlparse.parse(l)
