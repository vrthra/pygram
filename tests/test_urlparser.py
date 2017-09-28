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
$_PARSENOCACHE:POSTPARSE_@ ::= $_PARSENOCACHE:TOKENS
	| $__INIT__:MATCHSTRING
$__GETATTR__:__GETITEM___@ ::= $__GETITEM__:__GETITEM___@
$__INIT__:MATCHSTRING ::= $POSTPARSE:TOKENLIST
$_PARSENOCACHE:TOKENS ::= $POSTPARSE:TOKENLIST
$__GETITEM__:__GETITEM___@ ::= $URLSPLIT:__GETATTR___@
	| $__SETITEM__:__GETITEM___@
$POSTPARSE:TOKENLIST ::= $_ASSTRINGLIST:ITEM
	| $__INIT__:TOKLIST
$__SETITEM__:__GETITEM___@ ::= $<LISTCOMP>:__GETITEM___@
$URLSPLIT:__GETATTR___@ ::= $__DELITEM__:VALUE
$_ASSTRINGLIST:ITEM ::= $__NEW__:TOKLIST
$__INIT__:TOKLIST ::= $__NEW__:TOKLIST
$<LISTCOMP>:__GETITEM___@ ::= $__IADD__:__GETITEM___@
$__DELITEM__:VALUE ::= $__SETITEM__:SUB
$__NEW__:TOKLIST ::= $LITERAL.MATCH
	| cs
	| de
	| st
	| uni-saarland
	| www
$__IADD__:__GETITEM___@ ::= $__SETITEM__:V
$__SETITEM__:SUB ::= $__SETITEM__:V
$LITERAL.MATCH ::= //
$__SETITEM__:V ::= $__INIT__:P1
$__INIT__:P1 ::= /zeller#ref
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
$START ::= $__DELITEM__:__GETITEM___@:$_PARSENOCACHE:POSTPARSE_@$_PARSENOCACHE:POSTPARSE_@.$_PARSENOCACHE:POSTPARSE_@$__DELITEM__:__GETITEM___@?$_PARSENOCACHE:POSTPARSE_@#$_PARSENOCACHE:POSTPARSE_@
	| $__DELITEM__:__GETITEM___@:$_PARSENOCACHE:POSTPARSE_@$_PARSENOCACHE:POSTPARSE_@.$_PARSENOCACHE:POSTPARSE_@.$_PARSENOCACHE:POSTPARSE_@$__DELITEM__:__GETITEM___@
	| http://$URLPARSE:NETLOC/zeller#ref
$URLPARSE:NETLOC ::= www.st.cs.uni-saarland.de
$__DELITEM__:__GETITEM___@ ::= $__GETATTR__:__GETITEM___@
$_PARSENOCACHE:POSTPARSE_@ ::= $URLSPLIT:__GETITEM___@
	| $_PARSENOCACHE:TOKENS
$__GETATTR__:__GETITEM___@ ::= $__GETITEM__:__GETITEM___@
$_PARSENOCACHE:TOKENS ::= $POSTPARSE:TOKENLIST
$__GETITEM__:__GETITEM___@ ::= $URLSPLIT:__GETATTR___@
	| $__SETITEM__:__GETITEM___@
$POSTPARSE:TOKENLIST ::= $_ASSTRINGLIST:ITEM
	| $__INIT__:TOKLIST
$__SETITEM__:__GETITEM___@ ::= $<LISTCOMP>:__GETITEM___@
$URLSPLIT:__GETATTR___@ ::= $__DELITEM__:VALUE
$_ASSTRINGLIST:ITEM ::= $URLPARSE:FRAGMENT
	| $__NEW__:TOKLIST
$__INIT__:TOKLIST ::= $__NEW__:TOKLIST
$<LISTCOMP>:__GETITEM___@ ::= $__IADD__:__GETITEM___@
$__DELITEM__:VALUE ::= $__SETITEM__:SUB
$__NEW__:TOKLIST ::= $LITERAL.MATCH
	| $URLPARSE:QUERY
	| cispa
	| com:8080
	| foo@google
	| saarland:80
	| www
$__IADD__:__GETITEM___@ ::= $__SETITEM__:V
$__SETITEM__:SUB ::= $__SETITEM__:V
$LITERAL.MATCH ::= //
$__SETITEM__:V ::= $__INIT__:P1
$__INIT__:P1 ::= /bar
	| http
	| https
$URLSPLIT:__GETITEM___@ ::= $POSTPARSE:TOKENLIST
$URLPARSE:FRAGMENT ::= ref2
$URLPARSE:QUERY ::= q=r
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

