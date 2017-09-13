import pgn
import induce, helpers

tpgn = helpers.slurparg()
with induce.grammar() as g:
  with induce.Tracer(tpgn, g):
    tokens = pgn.pgnGrammar.parseString(tpgn)
    print "tokens = ", tokens
