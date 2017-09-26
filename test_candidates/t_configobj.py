import configobj
import induce, helpers

with induce.grammar() as g:
    ini = helpers.slurparg()
    with induce.Tracer(ini, g):
       config = configobj.ConfigObj(ini)
    #print config

