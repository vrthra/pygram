import urlparser
import induce
import collections
import random
random.seed(0)


def test_urlparser():
    url_lines = '''
http://www.st.cs.uni-saarland.de/zeller#ref
https://www.cispa.saarland:80/bar
http://foo@google.com:8080/bar?q=r#ref2
'''[1:-1]
    grammar = '''
$START ::= $SCHEME:$MATCHSTRING$NETLOC$URL
	| $INSTRING
	| $SCHEME://$NETLOC$URL?$QUERY#$TOKENS
$MATCHSTRING ::= //
$NETLOC ::= www.st.cs.uni-saarland.de
	| www.cispa.saarland:80
	| foo@google.com:8080
$SCHEME ::= http
	| https
$URL ::= $TOKENS
	| $V
$TOKENS ::= $TOKENLIST
$TOKENLIST ::= $TOKLIST
$TOKLIST ::= $V
	| $ITEM
$V ::= $P1
$P1 ::= $SUB
$SUB ::= $ITEM
	| $VALUE
$ITEM ::= $VALUE
	| $FRAGMENT
$VALUE ::= /zeller#ref
	| /bar
$INSTRING ::= $PSTR
$PSTR ::= $SCHEME://$NETLOC$URL
$QUERY ::= q=r
$FRAGMENT ::= ref2
'''[1:-1]
    result = []
    for url in url_lines.split('\n'):
        with induce.Tracer(url, result) as t:
            urlparser.urlparse(url)
    assert(len(result) == 29840) # 31300)

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

