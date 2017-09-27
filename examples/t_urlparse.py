from urllib.parse import urlparse
import induce.helpers, induce

for l in induce.slurplstriparg():
    with induce.Tracer(l):
        urlparse(l)
