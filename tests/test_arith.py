import induce
import collections
import random
import arith
random.seed(0)


def test_arith1():
    arith_lines = '''
( AAAA - BBBB ) == 0
'''[1:-1]
    grammar = '''
$START ::= ( $_PARSENOCACHE:POSTPARSE_@ - $_PARSENOCACHE:POSTPARSE_@ ) $OPERATOROPERANDS:O1 0
$_PARSENOCACHE:POSTPARSE_@ ::= $__INIT__:__GETITEM___@
$OPERATOROPERANDS:O1 ::= $__INIT__:TOKLIST
$__INIT__:__GETITEM___@ ::= $_PARSENOCACHE:TOKENS
$__INIT__:TOKLIST ::= $__NEW__:TOKLIST
$_PARSENOCACHE:TOKENS ::= $POSTPARSE:TOKENLIST
$__NEW__:TOKLIST ::= ==
$POSTPARSE:TOKENLIST ::= $EVALCONSTANT.VALUE
$EVALCONSTANT.VALUE ::= AAAA
	| BBBB
'''[1:-1]
    result = []
    rules = arith_lines.split('\n')
    myvars={'AAAA': 0, 'BBBB': 1.1, 'CCCC': 2.2, 'DDDD': 3.3, 'EEEE': 4.4, 'FFFF': 5.5, 'GGGG':
                   6.6, 'HHHH':7.7, 'IIII':8.8, 'JJJJ':9.9, "abc": 20, }

    # define tests from given rules
    tests = [(t, eval(t,myvars)) for t in rules if t.strip() != '']
    myarith = arith.Arith(myvars)
    for test,expected in tests:
        with induce.Tracer(test, result):
             res = myarith.eval( test )
             #print(test,expected,"<>",res)

    with induce.grammar() as g:
        for jframe in result:
            g.handle_events(jframe)
        print(str(g))
        assert(grammar == str(g))

def test_arith2():
    arith_lines = '''
( AAAA - BBBB ) == 0
BBBB * ( CCCC + DDDD )
(BBBB + CCCC ) - DDDD
'''[1:-1]
    grammar = '''
$START ::= $_PARSENOCACHE:POSTPARSE_@ * ( $_PARSENOCACHE:POSTPARSE_@ + $_PARSENOCACHE:POSTPARSE_@ )
	| ( $_PARSENOCACHE:POSTPARSE_@ - $_PARSENOCACHE:POSTPARSE_@ ) $OPERATOROPERANDS:O1 0
	| ($_PARSENOCACHE:POSTPARSE_@ + $_PARSENOCACHE:POSTPARSE_@ ) - $_PARSENOCACHE:POSTPARSE_@
$_PARSENOCACHE:POSTPARSE_@ ::= $__INIT__:__GETITEM___@
$OPERATOROPERANDS:O1 ::= $__INIT__:TOKLIST
$__INIT__:__GETITEM___@ ::= $_PARSENOCACHE:TOKENS
$__INIT__:TOKLIST ::= $__NEW__:TOKLIST
$_PARSENOCACHE:TOKENS ::= $POSTPARSE:TOKENLIST
$__NEW__:TOKLIST ::= $EVALCONSTANT.VALUE
	| ==
$POSTPARSE:TOKENLIST ::= $EVALCONSTANT.VALUE
	| $__INIT__:TOKLIST
$EVALCONSTANT.VALUE ::= AAAA
	| BBBB
	| CCCC
	| DDDD
'''[1:-1]
    result = []
    rules = arith_lines.split('\n')
    myvars={'AAAA': 0, 'BBBB': 1.1, 'CCCC': 2.2, 'DDDD': 3.3, 'EEEE': 4.4, 'FFFF': 5.5, 'GGGG':
                   6.6, 'HHHH':7.7, 'IIII':8.8, 'JJJJ':9.9, "abc": 20, }

    # define tests from given rules
    tests = [(t, eval(t,myvars)) for t in rules if t.strip() != '']
    myarith = arith.Arith(myvars)
    for test,expected in tests:
        with induce.Tracer(test, result):
             res = myarith.eval( test )
             #print(test,expected,"<>",res)

    with induce.grammar() as g:
        for jframe in result:
            g.handle_events(jframe)
        print(str(g))
        assert(grammar == str(g))

