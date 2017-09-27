from urllib.parse import urlparse
import induce
import collections
import random
random.seed(0)


def test_urlparse1():
    url_lines = '''
http://www.st.cs.uni-saarland.de/zeller#ref
'''[1:-1]
    grammar = '''
$START ::= $SCHEME://$NETLOC$URL#$FRAGMENT
$URL ::= $PATH
$SCHEME ::= http
$NETLOC ::= www.st.cs.uni-saarland.de
$FRAGMENT ::= ref
$PATH ::= /zeller
'''[1:-1]
    result = []
    for url in url_lines.split('\n'):
        with induce.Tracer(url, result) as t:
            urlparse(url)
    assert(len(result) == 78)

    with induce.grammar() as g:
        for count, jframe in enumerate(result):
            if len(jframe) == 0:
                g.reset()
            else:
                myframe = collections.OrderedDict()
                for k in sorted(jframe.keys()): myframe[k] = jframe[k]
                g.update(myframe)
        print(str(g))
        assert(grammar == str(g))

def test_urlparse2():
    url_lines = '''
http://www.st.cs.uni-saarland.de/zeller#ref
https://www.cispa.saarland:80/bar
http://foo@google.com:8080/bar?q=r#ref2
'''[1:-1]
    grammar = '''
$START ::= $SCHEME://$NETLOC$URL#$FRAGMENT
	| $SCHEME://$NETLOC$URL
	| $SCHEME://$NETLOC$URL?$QUERY#$FRAGMENT
$URL ::= $PATH
$FRAGMENT ::= ref
	| ref2
$NETLOC ::= www.st.cs.uni-saarland.de
	| www.cispa.saarland:80
	| foo@google.com:8080
$SCHEME ::= http
	| https
$PATH ::= /zeller
	| /bar
$QUERY ::= q=r
'''[1:-1]
    result = []
    for url in url_lines.split('\n'):
        with induce.Tracer(url, result) as t:
            urlparse(url)
    assert(len(result) == 217)

    with induce.grammar() as g:
        for count, jframe in enumerate(result):
            if len(jframe) == 0:
                g.reset()
            else:
                myframe = collections.OrderedDict()
                for k in sorted(jframe.keys()): myframe[k] = jframe[k]
                g.update(myframe)
        print(str(g))
        assert(grammar == str(g))

