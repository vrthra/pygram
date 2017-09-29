import simplejson
import induce

myfile = induce.slurparg()
with induce.Tracer(myfile):
    simplejson.loads(myfile)

