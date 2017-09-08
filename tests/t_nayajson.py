import induce, helpers
import nayajson

with induce.grammar() as g:
    myfile = helpers.slurparg()
    with induce.Tracer(myfile, g):
        nayajson.parse_string(myfile)

