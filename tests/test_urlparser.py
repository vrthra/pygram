import urlparser
import induce, induce.helpers
import json
import induce
import sys
import pdb;


def test_urlparser():
    url_lines = '''
http://www.st.cs.uni-saarland.de/zeller#ref
https://www.cispa.saarland:80/bar
http://foo@google.com:8080/bar?q=r#ref2
    '''[1:-1]
    grammar = '''
$START ::= $INSTRING
	| $PSTR
	| $URL
$URL ::= $TOKENS:$MATCHSTRING$TOKENS.$TOKENS.$TOKENS.$TOKENS.$TOKENS$TOKENS
	| $TOKENS:$TOKENS$TOKENS.$TOKENS.$TOKENS$TOKENS
	| $INSTRING
	| $TOKENS
$MATCHSTRING ::= $TOKENLIST
$TOKENS ::= $TOKENLIST
$TOKENLIST ::= $TOKLIST
$TOKLIST ::= $ITEM
	| //
	| $V
$ITEM ::= uni-saarland
	| saarland:80
	| foo@google
	| $FRAGMENT
	| com:8080
	| $NETLOC
	| $QUERY
	| cispa
	| www
	| $P1
	| st
	| cs
	| de
$V ::= $P1
$NETLOC ::= www.st.cs.uni-saarland.de
	| www.cispa.saarland:80
	| foo@google.com:8080
$P1 ::= $SUB
$SUB ::= $VALUE
$VALUE ::= /zeller#ref
	| $SCHEME
	| /bar
$SCHEME ::= https
	| http
$INSTRING ::= $TOKENLIST:$TOKENLIST$TOKENLIST.$TOKENLIST$TOKENLIST?$TOKENLIST#$TOKENLIST
	| $PSTR
	|    
$PSTR ::= $URL
$FRAGMENT ::= ref2
$QUERY ::= q=r
'''[1:-1]
    result = []
    for url in url_lines.split('\n'):
        with induce.Tracer(url, result) as t:
            urlparser.urlparse(url)
    assert(len(result) == 31300)

    with induce.grammar() as g:
        for count, jframe in enumerate(result):
            if len(jframe) == 0:
                g.reset()
            else:
                g.update(jframe)
        assert(grammar == str(g))

