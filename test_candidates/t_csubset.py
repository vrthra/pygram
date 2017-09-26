
import csubset
import pprint
import helpers, induce

test = helpers.slurparg()
with induce.grammar() as g:
  ast = None
  with induce.Tracer(test, g):
     ast = csubset.program.parseString(test, parseAll=True)
  pprint.pprint(ast.asList())
