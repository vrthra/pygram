import configobj
import induce

ini = induce.slurparg()
with induce.Tracer(ini):
    config = configobj.ConfigObj(ini)
    print(config)

