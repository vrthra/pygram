import urlparser
import induce
import collections
import random
random.seed(0)


def xtest_urlparser1():
    url_lines = '''
http://www.st.cs.uni-saarland.de/zeller#ref
'''[1:-1]
    grammar = '''
$VALUE ::= $SCHEME
$URL ::= $V
	| $TOKENS
$MATCHSTRING ::= //
$P1 ::= $VALUE
$START ::= $P1:$MATCHSTRING$NETLOC$TOKLIST
	| $P1://$NETLOC$SUB?$QUERY#$TOKLIST
	| $P1://$NETLOC$TOKLIST
$NETLOC ::= foo@google.com:8080
	| www.st.cs.uni-saarland.de
	| www.cispa.saarland:80
$TOKLIST ::= $OBJ
$TOKENLIST ::= $V
	| ref2
$QUERY ::= q=r
$TOKENS ::= $ITEM
$ITEM ::= $TOKENLIST
$SCHEME ::= http
	| https
$V ::= /zeller#ref
	| /bar
$OBJ ::= $FRAGMENT
	| $SUB
$FRAGMENT ::= $TOKENS
$SUB ::= $URL
'''[1:-1]
    result = []
    for url in url_lines.split('\n'):
        with induce.Tracer(url, result) as t:
            urlparser.urlparse(url)
    assert(len(result) == 2031) # 31300)

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

def xtest_urlparser2():
    url_lines = '''
http://www.st.cs.uni-saarland.de/zeller#ref
https://www.cispa.saarland:80/bar
http://foo@google.com:8080/bar?q=r#ref2
'''[1:-1]
    grammar = '''
$VALUE ::= $SCHEME
$URL ::= $V
	| $TOKENS
$MATCHSTRING ::= //
$P1 ::= $VALUE
$START ::= $P1:$MATCHSTRING$NETLOC$TOKLIST
	| $P1://$NETLOC$SUB?$QUERY#$TOKLIST
	| $P1://$NETLOC$TOKLIST
$NETLOC ::= foo@google.com:8080
	| www.st.cs.uni-saarland.de
	| www.cispa.saarland:80
$TOKLIST ::= $OBJ
$TOKENLIST ::= $V
	| ref2
$QUERY ::= q=r
$TOKENS ::= $ITEM
$ITEM ::= $TOKENLIST
$SCHEME ::= http
	| https
$V ::= /zeller#ref
	| /bar
$OBJ ::= $FRAGMENT
	| $SUB
$FRAGMENT ::= $TOKENS
$SUB ::= $URL
'''[1:-1]
    result = []
    for url in url_lines.split('\n'):
        with induce.Tracer(url, result) as t:
            urlparser.urlparse(url)
    assert(len(result) == 7309) # 31300)

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

