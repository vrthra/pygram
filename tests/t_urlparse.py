from urlparse import urlparse
import induce

data='''\
http://www.st.cs.uni-saarland.de/zeller#ref
https://www.cispa.saarland:80/bar
http://foo@google.com:8080/bar?q=r#ref2\
'''

with induce.Tracer():
    for l in data.split('\n'):
        print(l)
        urlparse(l)
