import microjson
import induce

myfile = induce.slurparg()
with induce.Tracer(myfile):
    microjson.from_json(myfile)

