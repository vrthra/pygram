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
$FRAGMENT ::= ref
$NETLOC ::= www.st.cs.uni-saarland.de
$START ::= $__NEW__:SCHEME://$__NEW__:NETLOC$__NEW__:PATH#$__NEW__:FRAGMENT
$__NEW__:FRAGMENT ::= $FRAGMENT
$__NEW__:NETLOC ::= $NETLOC
$__NEW__:PATH ::= /zeller
$__NEW__:SCHEME ::= http
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
$FRAGMENT ::= ref
	| ref2
$NETLOC ::= foo@google.com:8080
	| www.cispa.saarland:80
	| www.st.cs.uni-saarland.de
$QUERY ::= q=r
$START ::= $__NEW__:SCHEME:$_SPLITNETLOC:URL
	| $__NEW__:SCHEME://$__NEW__:NETLOC$__NEW__:PATH#$__NEW__:FRAGMENT
	| $__NEW__:SCHEME://$__NEW__:NETLOC$__NEW__:PATH?$__NEW__:QUERY#$__NEW__:FRAGMENT
$_SPLITNETLOC:URL ::= //$__NEW__:NETLOC$__NEW__:PATH
$__NEW__:FRAGMENT ::= $FRAGMENT
$__NEW__:NETLOC ::= $NETLOC
$__NEW__:PATH ::= /bar
	| /zeller
$__NEW__:QUERY ::= $QUERY
$__NEW__:SCHEME ::= http
	| https
'''[1:-1]
    result = []
    for url in url_lines.split('\n'):
        with induce.Tracer(url, result) as t:
            urlparse(url)

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

