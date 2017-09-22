import urlparser
import induce
data='''\
      http://a/b/c/d

      g          = <URL:http://a/b/c/g>
      g:h        = <URL:g:h>
      http:g     = <URL:http://a/b/c/g>
      http:      = <URL:http://a/b/c/d>
      ./g        = <URL:http://a/b/c/g>
      g/         = <URL:http://a/b/c/g/>
      /g         = <URL:http://a/g>
      //g        = <URL:http://g>
      ?y         = <URL:http://a/b/c/d?y>
      g?y        = <URL:http://a/b/c/g?y>
      g?y/./x    = <URL:http://a/b/c/g?y/./x>
      .          = <URL:http://a/b/c/>
      ./         = <URL:http://a/b/c/>
      ..         = <URL:http://a/b/>
      ../        = <URL:http://a/b/>
      ../g       = <URL:http://a/b/g>
      ../..      = <URL:http://a/>
      ../../g    = <URL:http://a/g>
      ../../../g = <URL:http://a/../g>
      ./../g     = <URL:http://a/b/g>
      ./g/.      = <URL:http://a/b/c/g/>
      /./g       = <URL:http://a/./g>
      g/./h      = <URL:http://a/b/c/g/h>
      g/../h     = <URL:http://a/b/c/h>
      http:g     = <URL:http://a/b/c/g>
      http:      = <URL:http://a/b/c/d>
      http:?y         = <URL:http://a/b/c/d?y>
      http:g?y        = <URL:http://a/b/c/g?y>
      http://d.e.f/g?y        = <URL:http://d.e.f/g?y>
      http:g?y/./x    = <URL:http://a/b/c/g?y/./x>\
'''

base = ''
for line in data.split('\n'):
  words = line.split()
  if not words: continue
  url = words[0]
  with induce.Tracer():
     parts = urlparser.urlparse(url)
     #print '%-10s : %s' % (url, parts)
  #abs = urlparser.urljoin(base, url)
  #if not base: base = abs
  #wrapped = '<URL:%s>' % abs
  #print '%-10s = %s' % (url, wrapped)
  #if len(words) == 3 and words[1] == '=':
  #    if wrapped != words[2]:
  #        print 'EXPECTED', words[2], '!!!!!!!!!!'

