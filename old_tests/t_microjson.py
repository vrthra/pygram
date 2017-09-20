import microjson
import helpers, induce

with induce.grammar() as g:
    myfile = helpers.slurparg()
    with induce.Tracer(myfile, g):
        microjson.from_json(myfile)

