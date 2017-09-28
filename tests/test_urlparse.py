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
$START ::= $__NEW__:SCHEME://$URLPARSE:NETLOC$__NEW__:PATH#$URLPARSE:FRAGMENT
$URLPARSE:FRAGMENT ::= $URLSPLIT:FRAGMENT
$URLPARSE:NETLOC ::= $URLSPLIT:NETLOC
$__NEW__:SCHEME ::= http
$__NEW__:PATH ::= /zeller
$URLSPLIT:FRAGMENT ::= $__NEW__:FRAGMENT
$URLSPLIT:NETLOC ::= $__NEW__:NETLOC
$__NEW__:FRAGMENT ::= ref
$__NEW__:NETLOC ::= www.st.cs.uni-saarland.de
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
	| $__NEW__:SCHEME://$URLPARSE:NETLOC$__NEW__:PATH#$URLPARSE:FRAGMENT
	| $__NEW__:SCHEME://$URLPARSE:NETLOC$__NEW__:PATH?$URLPARSE:QUERY#$URLPARSE:FRAGMENT
$URLPARSE:FRAGMENT ::= $URLSPLIT:FRAGMENT
	| $__NEW__:FRAGMENT
$URLPARSE:NETLOC ::= $URLSPLIT:NETLOC
	| $__NEW__:NETLOC
$__NEW__:SCHEME ::= http
	| https
$__NEW__:PATH ::= /bar
	| /zeller
$__NEW__:FRAGMENT ::= ref
	| ref2
$__NEW__:NETLOC ::= foo@google.com:8080
	| www.cispa.saarland:80
	| www.st.cs.uni-saarland.de
$_SPLITNETLOC:URL ::= //$URLPARSE:NETLOC$__NEW__:PATH
$URLSPLIT:NETLOC ::= $__NEW__:NETLOC
$URLPARSE:QUERY ::= $URLSPLIT:QUERY
$URLSPLIT:FRAGMENT ::= $__NEW__:FRAGMENT
$URLSPLIT:QUERY ::= $__NEW__:QUERY
$__NEW__:QUERY ::= q=r
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

