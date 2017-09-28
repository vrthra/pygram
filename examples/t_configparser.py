import configparser
import induce

ini = induce.slurparg()
with induce.Tracer(ini):
    config = configparser.ConfigParser(allow_no_value=True)
    config.read_string(ini)
