import simplejson
import helpers, induce

with induce.grammar() as g:
    myfile = helpers.slurparg()
    with induce.Tracer(myfile, g):
        simplejson.loads(myfile)

