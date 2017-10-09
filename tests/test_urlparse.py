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
$START ::= $PARSERESULT.__NEW__:SCHEME://$PARSERESULT.__NEW__:NETLOC$PARSERESULT.__NEW__:PATH#$PARSERESULT.__NEW__:FRAGMENT
$PARSERESULT.__NEW__:FRAGMENT ::= $SPLITRESULT.__NEW__:FRAGMENT
$PARSERESULT.__NEW__:NETLOC ::= $SPLITRESULT.__NEW__:NETLOC
$PARSERESULT.__NEW__:SCHEME ::= $SPLITRESULT.__NEW__:SCHEME
$PARSERESULT.__NEW__:PATH ::= $SPLITRESULT.__NEW__:PATH
$SPLITRESULT.__NEW__:FRAGMENT ::= $@.URLPARSE:FRAGMENT
$SPLITRESULT.__NEW__:NETLOC ::= $@.URLPARSE:NETLOC
$SPLITRESULT.__NEW__:SCHEME ::= http
$SPLITRESULT.__NEW__:PATH ::= /zeller
$@.URLPARSE:FRAGMENT ::= $@.URLSPLIT:FRAGMENT
$@.URLPARSE:NETLOC ::= $@.URLSPLIT:NETLOC
$@.URLSPLIT:FRAGMENT ::= ref
$@.URLSPLIT:NETLOC ::= www.st.cs.uni-saarland.de
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
$START ::= $PARSERESULT.__NEW__:SCHEME://$PARSERESULT.__NEW__:NETLOC$PARSERESULT.__NEW__:PATH
	| $PARSERESULT.__NEW__:SCHEME://$PARSERESULT.__NEW__:NETLOC$PARSERESULT.__NEW__:PATH#$PARSERESULT.__NEW__:FRAGMENT
	| $PARSERESULT.__NEW__:SCHEME://$PARSERESULT.__NEW__:NETLOC$PARSERESULT.__NEW__:PATH?$PARSERESULT.__NEW__:QUERY#$PARSERESULT.__NEW__:FRAGMENT
$PARSERESULT.__NEW__:FRAGMENT ::= $@.URLPARSE:FRAGMENT
	| $SPLITRESULT.__NEW__:FRAGMENT
$PARSERESULT.__NEW__:NETLOC ::= $@.URLPARSE:NETLOC
	| $SPLITRESULT.__NEW__:NETLOC
$PARSERESULT.__NEW__:SCHEME ::= $SPLITRESULT.__NEW__:SCHEME
	| http
$PARSERESULT.__NEW__:PATH ::= $SPLITRESULT.__NEW__:PATH
	| /zeller
$@.URLPARSE:FRAGMENT ::= $@.URLSPLIT:FRAGMENT
	| ref
$@.URLPARSE:NETLOC ::= $@.URLSPLIT:NETLOC
	| www.st.cs.uni-saarland.de
$SPLITRESULT.__NEW__:NETLOC ::= $@.URLPARSE:NETLOC
$SPLITRESULT.__NEW__:SCHEME ::= http
	| https
$SPLITRESULT.__NEW__:PATH ::= /bar
$@.URLSPLIT:NETLOC ::= foo@google.com:8080
	| www.cispa.saarland:80
$PARSERESULT.__NEW__:QUERY ::= $SPLITRESULT.__NEW__:QUERY
$SPLITRESULT.__NEW__:FRAGMENT ::= $@.URLPARSE:FRAGMENT
$SPLITRESULT.__NEW__:QUERY ::= $@.URLPARSE:QUERY
$@.URLPARSE:QUERY ::= $@.URLSPLIT:QUERY
$@.URLSPLIT:FRAGMENT ::= ref2
$@.URLSPLIT:QUERY ::= q=r
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
