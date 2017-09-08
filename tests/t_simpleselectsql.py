import simpleselectsql
import induce, helpers

with induce.grammar() as g:
    for i in helpers.slurplstriparg():
       with induce.Tracer(i, g):
          simpleselectsql.selectStmt.parseString(i)
