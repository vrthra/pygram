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
$<LISTCOMP>:__GETITEM___@ ::= $__IADD__:__GETITEM___@
$ITEM ::= cs
	| de
	| st
	| uni-saarland
	| www
$LITERAL.MATCH ::= //
$POSTPARSE:TOKENLIST ::= $__INIT__:TOKLIST
$START ::= $__DELITEM__:__GETITEM___@:$_PARSENOCACHE:POSTPARSE_@$_PARSENOCACHE:POSTPARSE_@.$_PARSENOCACHE:POSTPARSE_@.$_PARSENOCACHE:POSTPARSE_@.$_PARSENOCACHE:POSTPARSE_@.$_PARSENOCACHE:POSTPARSE_@$__DELITEM__:__GETITEM___@
$SUB ::= /zeller#ref
	| http
$TOKENS ::= $ITEM
	| $LITERAL.MATCH
$URLSPLIT:__GETATTR___@ ::= $__SETITEM__:V
$VALUE ::= $SUB
$_PARSENOCACHE:POSTPARSE_@ ::= $POSTPARSE:TOKENLIST
	| $__INIT__:MATCHSTRING
$__DELITEM__:__GETITEM___@ ::= $__GETATTR__:__GETITEM___@
$__GETATTR__:__GETITEM___@ ::= $__GETITEM__:__GETITEM___@
$__GETITEM__:__GETITEM___@ ::= $URLSPLIT:__GETATTR___@
	| $__SETITEM__:__GETITEM___@
$__IADD__:__GETITEM___@ ::= $VALUE
$__INIT__:MATCHSTRING ::= $__INIT__:TOKLIST
$__INIT__:P1 ::= $VALUE
$__INIT__:TOKLIST ::= $__NEW__:TOKLIST
$__NEW__:TOKLIST ::= $TOKENS
$__SETITEM__:V ::= $__INIT__:P1
$__SETITEM__:__GETITEM___@ ::= $<LISTCOMP>:__GETITEM___@
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
$<LISTCOMP>:__GETITEM___@ ::= $__IADD__:__GETITEM___@
$FRAGMENT ::= $ITEM
$ITEM ::= cispa
	| com:8080
	| foo@google
	| ref2
	| saarland:80
	| www
$LITERAL.MATCH ::= //
$NETLOC ::= www.st.cs.uni-saarland.de
$POSTPARSE:TOKENLIST ::= $__INIT__:TOKLIST
$QUERY ::= q=r
$START ::= $URLPARSE:URL
	| $__DELITEM__:__GETITEM___@:$_PARSENOCACHE:POSTPARSE_@$_PARSENOCACHE:POSTPARSE_@.$_PARSENOCACHE:POSTPARSE_@$__DELITEM__:__GETITEM___@?$_PARSENOCACHE:POSTPARSE_@#$_PARSENOCACHE:POSTPARSE_@
	| $__DELITEM__:__GETITEM___@:$_PARSENOCACHE:POSTPARSE_@$_PARSENOCACHE:POSTPARSE_@.$_PARSENOCACHE:POSTPARSE_@.$_PARSENOCACHE:POSTPARSE_@$__DELITEM__:__GETITEM___@
$SUB ::= /bar
	| http
	| https
$TOKENS ::= $ITEM
	| $LITERAL.MATCH
	| $QUERY
$URLPARSE:URL ::= $URLSPLIT:URL
$URLSPLIT:URL ::= http://$NETLOC/zeller#ref
$URLSPLIT:__GETATTR___@ ::= $__SETITEM__:V
$URLSPLIT:__GETITEM___@ ::= $__INIT__:TOKLIST
$VALUE ::= $SUB
$_PARSENOCACHE:POSTPARSE_@ ::= $POSTPARSE:TOKENLIST
	| $URLSPLIT:__GETITEM___@
$__DELITEM__:__GETITEM___@ ::= $__GETATTR__:__GETITEM___@
$__GETATTR__:__GETITEM___@ ::= $__GETITEM__:__GETITEM___@
$__GETITEM__:__GETITEM___@ ::= $URLSPLIT:__GETATTR___@
	| $__SETITEM__:__GETITEM___@
$__IADD__:__GETITEM___@ ::= $VALUE
$__INIT__:P1 ::= $VALUE
$__INIT__:TOKLIST ::= $__NEW__:TOKLIST
$__NEW__:TOKLIST ::= $FRAGMENT
	| $TOKENS
$__SETITEM__:V ::= $__INIT__:P1
$__SETITEM__:__GETITEM___@ ::= $<LISTCOMP>:__GETITEM___@
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

