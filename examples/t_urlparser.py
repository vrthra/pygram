import urlparser
import induce, induce.helpers

base = ''
for line in induce.helpers.slurplarg():
    words = line.split()
    if not words: continue
    url = words[0]
    with induce.Tracer(url):
       parts = urlparser.urlparse(url)
