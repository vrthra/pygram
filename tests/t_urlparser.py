import urlparser
import induce, induce.helpers

with induce.grammar() as g:
  base = ''
  for line in induce.helpers.slurplarg():
    words = line.split()
    if not words: continue
    url = words[0]
    with induce.Tracer(url, g):
       parts = urlparser.urlparse(url)
       #print '%-10s : %s' % (url, parts)
    #abs = urlparser.urljoin(base, url)
    #if not base: base = abs
    #wrapped = '<URL:%s>' % abs
    #print '%-10s = %s' % (url, wrapped)
    #if len(words) == 3 and words[1] == '=':
    #    if wrapped != words[2]:
    #        print 'EXPECTED', words[2], '!!!!!!!!!!'

