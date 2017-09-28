import urlparser
import induce
import collections
import random
random.seed(0)


def test_urlparser1():
    url_lines = '''
http://www.st.cs.uni-saarland.de/zeller#ref
'''[1:-1]
    grammar = '''
$START ::= $__DELITEM__:__GETITEM___@:$_PARSENOCACHE:POSTPARSE_@$_PARSENOCACHE:POSTPARSE_@.$_PARSENOCACHE:POSTPARSE_@.$_PARSENOCACHE:POSTPARSE_@.$_PARSENOCACHE:POSTPARSE_@.$_PARSENOCACHE:POSTPARSE_@$__DELITEM__:__GETITEM___@
$__DELITEM__:__GETITEM___@ ::= $__GETATTR__:__GETITEM___@
$_PARSENOCACHE:POSTPARSE_@ ::= $POSTPARSE:TOKENLIST
	| $__INIT__:MATCHSTRING
$__GETATTR__:__GETITEM___@ ::= $__GETITEM__:__GETITEM___@
$__INIT__:MATCHSTRING ::= $__INIT__:TOKLIST
$POSTPARSE:TOKENLIST ::= $__INIT__:TOKLIST
$__GETITEM__:__GETITEM___@ ::= $URLSPLIT:__GETATTR___@
	| $__SETITEM__:__GETITEM___@
$__INIT__:TOKLIST ::= $__NEW__:TOKLIST
$__SETITEM__:__GETITEM___@ ::= $<LISTCOMP>:__GETITEM___@
$URLSPLIT:__GETATTR___@ ::= $__SETITEM__:V
$__NEW__:TOKLIST ::= $TOKENS
$<LISTCOMP>:__GETITEM___@ ::= $__IADD__:__GETITEM___@
$__SETITEM__:V ::= $__INIT__:P1
$TOKENS ::= $ITEM
	| $LITERAL.MATCH
$__IADD__:__GETITEM___@ ::= $VALUE
$__INIT__:P1 ::= $VALUE
$ITEM ::= cs
	| de
	| st
	| uni-saarland
	| www
$LITERAL.MATCH ::= //
$VALUE ::= $SUB
$SUB ::= /zeller#ref
	| http
'''[1:-1]
    result = []
    for url in url_lines.split('\n'):
        with induce.Tracer(url, result) as t:
            urlparser.urlparse(url)
    with induce.grammar() as g:
        for jframe in result:
            g.handle_events(jframe)
        print(str(g))
        assert(grammar == str(g))

def test_urlparser2():
    url_lines = '''
http://www.st.cs.uni-saarland.de/zeller#ref
https://www.cispa.saarland:80/bar
http://foo@google.com:8080/bar?q=r#ref2
'''[1:-1]
    grammar = '''
$START ::= $URLPARSE:URL
	| $__DELITEM__:__GETITEM___@:$_PARSENOCACHE:POSTPARSE_@$_PARSENOCACHE:POSTPARSE_@.$_PARSENOCACHE:POSTPARSE_@$__DELITEM__:__GETITEM___@?$_PARSENOCACHE:POSTPARSE_@#$_PARSENOCACHE:POSTPARSE_@
	| $__DELITEM__:__GETITEM___@:$_PARSENOCACHE:POSTPARSE_@$_PARSENOCACHE:POSTPARSE_@.$_PARSENOCACHE:POSTPARSE_@.$_PARSENOCACHE:POSTPARSE_@$__DELITEM__:__GETITEM___@
$URLPARSE:URL ::= $URLSPLIT:URL
$URLSPLIT:URL ::= http://$NETLOC/zeller#ref
$NETLOC ::= www.st.cs.uni-saarland.de
$__DELITEM__:__GETITEM___@ ::= $__GETATTR__:__GETITEM___@
$_PARSENOCACHE:POSTPARSE_@ ::= $POSTPARSE:TOKENLIST
	| $URLSPLIT:__GETITEM___@
$__GETATTR__:__GETITEM___@ ::= $__GETITEM__:__GETITEM___@
$POSTPARSE:TOKENLIST ::= $__INIT__:TOKLIST
$__GETITEM__:__GETITEM___@ ::= $URLSPLIT:__GETATTR___@
	| $__SETITEM__:__GETITEM___@
$__INIT__:TOKLIST ::= $__NEW__:TOKLIST
$__SETITEM__:__GETITEM___@ ::= $<LISTCOMP>:__GETITEM___@
$URLSPLIT:__GETATTR___@ ::= $__SETITEM__:V
$__NEW__:TOKLIST ::= $FRAGMENT
	| $TOKENS
$<LISTCOMP>:__GETITEM___@ ::= $__IADD__:__GETITEM___@
$__SETITEM__:V ::= $__INIT__:P1
$TOKENS ::= $ITEM
	| $LITERAL.MATCH
	| $QUERY
$__IADD__:__GETITEM___@ ::= $VALUE
$__INIT__:P1 ::= $VALUE
$ITEM ::= cispa
	| com:8080
	| foo@google
	| ref2
	| saarland:80
	| www
$LITERAL.MATCH ::= //
$VALUE ::= $SUB
$SUB ::= /bar
	| http
	| https
$URLSPLIT:__GETITEM___@ ::= $__INIT__:TOKLIST
$FRAGMENT ::= $ITEM
$QUERY ::= q=r
'''[1:-1]
    result = []
    for url in url_lines.split('\n'):
        with induce.Tracer(url, result) as t:
            urlparser.urlparse(url)
    with induce.grammar() as g:
        for jframe in result:
            g.handle_events(jframe)
        print(str(g))
        assert(grammar == str(g))

