import configparser
import helpers, induce

with induce.grammar() as g:
   config = configparser.ConfigParser(allow_no_value=True)
   ini = helpers.slurparg()
   with induce.Tracer(ini,g):
        config.read_string(ini)
