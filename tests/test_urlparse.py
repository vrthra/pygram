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
$START ::= $__NEW__:SCHEME://$__NEW__:NETLOC$__NEW__:PATH#$__NEW__:FRAGMENT
$__NEW__:FRAGMENT ::= $FRAGMENT
$__NEW__:NETLOC ::= $NETLOC
$__NEW__:SCHEME ::= http
$__NEW__:PATH ::= /zeller
$FRAGMENT ::= ref
$NETLOC ::= www.st.cs.uni-saarland.de
'''[1:-1]
    result = []
    for url in url_lines.split('\n'):
        with induce.Tracer(url, result) as t:
            urlparse(url)

    with induce.grammar() as g:
        for jframe in result:
            g.handle_events(jframe)
        print(str(g))
        assert(grammar == str(g))

def test_urlparse2():
    url_lines = '''
http://www.st.cs.uni-saarland.de/zeller#ref
https://www.cispa.saarland:80/bar
http://foo@google.com:8080/bar?q=r#ref2
'''[1:-1]
    grammar = '''
$START ::= $__NEW__:SCHEME:$_SPLITNETLOC:URL
	| $__NEW__:SCHEME://$__NEW__:NETLOC$__NEW__:PATH#$__NEW__:FRAGMENT
	| $__NEW__:SCHEME://$__NEW__:NETLOC$__NEW__:PATH?$__NEW__:QUERY#$__NEW__:FRAGMENT
$__NEW__:FRAGMENT ::= $FRAGMENT
$__NEW__:NETLOC ::= $NETLOC
$__NEW__:SCHEME ::= http
	| https
$__NEW__:PATH ::= /bar
	| /zeller
$FRAGMENT ::= ref
	| ref2
$NETLOC ::= foo@google.com:8080
	| www.cispa.saarland:80
	| www.st.cs.uni-saarland.de
$_SPLITNETLOC:URL ::= //$__NEW__:NETLOC$__NEW__:PATH
$__NEW__:QUERY ::= $QUERY
$QUERY ::= q=r
'''[1:-1]
    result = []
    for url in url_lines.split('\n'):
        with induce.Tracer(url, result) as t:
            urlparse(url)

    with induce.grammar() as g:
        for jframe in result:
            g.handle_events(jframe)
        print(str(g))
        assert(grammar == str(g))

