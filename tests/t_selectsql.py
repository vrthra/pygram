import selectsql
import helpers, induce

with induce.grammar() as g:
  for t in helpers.slurplstriparg():
    print "<%s>" % t
    with induce.Tracer(t, g):
         selectsql.select_stmt.parseString(t)
