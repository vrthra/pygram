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
$START ::= $FOLLOWEDBY._PARSENOCACHE:INSTRING
$FOLLOWEDBY._PARSENOCACHE:INSTRING ::= $MATCHFIRST._PARSENOCACHE:INSTRING
$MATCHFIRST._PARSENOCACHE:INSTRING ::= $ONEORMORE._PARSENOCACHE:INSTRING
$ONEORMORE._PARSENOCACHE:INSTRING ::= $STRINGEND._PARSENOCACHE:INSTRING
$STRINGEND._PARSENOCACHE:INSTRING ::= $OPTIONAL._PARSENOCACHE:INSTRING
$OPTIONAL._PARSENOCACHE:INSTRING ::= $SUPPRESS._PARSENOCACHE:INSTRING
$SUPPRESS._PARSENOCACHE:INSTRING ::= $COMBINE._PARSENOCACHE:INSTRING
$COMBINE._PARSENOCACHE:INSTRING ::= $FORWARD._PARSENOCACHE:INSTRING
$FORWARD._PARSENOCACHE:INSTRING ::= $LITERAL._PARSENOCACHE:INSTRING
$LITERAL._PARSENOCACHE:INSTRING ::= $FOLLOWEDBY.PARSEIMPL:INSTRING
$FOLLOWEDBY.PARSEIMPL:INSTRING ::= $FOLLOWEDBY.POSTPARSE:INSTRING
$FOLLOWEDBY.POSTPARSE:INSTRING ::= $MATCHFIRST.PARSEIMPL:INSTRING
$MATCHFIRST.PARSEIMPL:INSTRING ::= $MATCHFIRST.POSTPARSE:INSTRING
$MATCHFIRST.POSTPARSE:INSTRING ::= ( $PARSERESULTS.__INIT__:TOKLIST - $PARSERESULTS.__INIT__:TOKLIST ) $PARSERESULTS.__INIT__:TOKLIST 0
$PARSERESULTS.__INIT__:TOKLIST ::= $PARSERESULTS.__NEW__:TOKLIST
$PARSERESULTS.__NEW__:TOKLIST ::= $@.OPERATOROPERANDS:O1
	| $WORD._PARSENOCACHE:TOKENS
$WORD._PARSENOCACHE:TOKENS ::= $WORD.POSTPARSE:TOKENLIST
$@.OPERATOROPERANDS:O1 ::= ==
$WORD.POSTPARSE:TOKENLIST ::= $EVALCONSTANT.VALUE
$EVALCONSTANT.VALUE ::= $EVALCONSTANT.__INIT__:PARSERESULTS.__GETITEM___@
$EVALCONSTANT.__INIT__:PARSERESULTS.__GETITEM___@ ::= $WORD._PARSENOCACHE:WORD.POSTPARSE_@
$WORD._PARSENOCACHE:WORD.POSTPARSE_@ ::= AAAA
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
$START ::= $FOLLOWEDBY._PARSENOCACHE:INSTRING
$FOLLOWEDBY._PARSENOCACHE:INSTRING ::= $MATCHFIRST._PARSENOCACHE:INSTRING
$MATCHFIRST._PARSENOCACHE:INSTRING ::= $ONEORMORE._PARSENOCACHE:INSTRING
$ONEORMORE._PARSENOCACHE:INSTRING ::= $STRINGEND._PARSENOCACHE:INSTRING
$STRINGEND._PARSENOCACHE:INSTRING ::= $OPTIONAL._PARSENOCACHE:INSTRING
	| $SUPPRESS._PARSENOCACHE:INSTRING
$OPTIONAL._PARSENOCACHE:INSTRING ::= $SUPPRESS._PARSENOCACHE:INSTRING
$SUPPRESS._PARSENOCACHE:INSTRING ::= $COMBINE._PARSENOCACHE:INSTRING
$COMBINE._PARSENOCACHE:INSTRING ::= $FORWARD._PARSENOCACHE:INSTRING
$FORWARD._PARSENOCACHE:INSTRING ::= $LITERAL._PARSENOCACHE:INSTRING
$LITERAL._PARSENOCACHE:INSTRING ::= $FOLLOWEDBY.PARSEIMPL:INSTRING
$FOLLOWEDBY.PARSEIMPL:INSTRING ::= $FOLLOWEDBY.POSTPARSE:INSTRING
$FOLLOWEDBY.POSTPARSE:INSTRING ::= $MATCHFIRST.PARSEIMPL:INSTRING
$MATCHFIRST.PARSEIMPL:INSTRING ::= $MATCHFIRST.POSTPARSE:INSTRING
$MATCHFIRST.POSTPARSE:INSTRING ::= $PARSERESULTS.__INIT__:TOKLIST * ( $PARSERESULTS.__INIT__:TOKLIST + $PARSERESULTS.__INIT__:TOKLIST )
	| ( $PARSERESULTS.__INIT__:TOKLIST - $PARSERESULTS.__INIT__:TOKLIST ) $PARSERESULTS.__INIT__:TOKLIST 0
	| ($PARSERESULTS.__INIT__:TOKLIST + $PARSERESULTS.__INIT__:TOKLIST ) - $PARSERESULTS.__INIT__:TOKLIST
$PARSERESULTS.__INIT__:TOKLIST ::= $PARSERESULTS.__NEW__:TOKLIST
$PARSERESULTS.__NEW__:TOKLIST ::= $@.OPERATOROPERANDS:O1
	| $WORD._PARSENOCACHE:TOKENS
$WORD._PARSENOCACHE:TOKENS ::= $WORD.POSTPARSE:TOKENLIST
$@.OPERATOROPERANDS:O1 ::= ==
$WORD.POSTPARSE:TOKENLIST ::= $EVALCONSTANT.VALUE
$EVALCONSTANT.VALUE ::= $EVALCONSTANT.__INIT__:PARSERESULTS.__GETITEM___@
$EVALCONSTANT.__INIT__:PARSERESULTS.__GETITEM___@ ::= $WORD._PARSENOCACHE:WORD.POSTPARSE_@
$WORD._PARSENOCACHE:WORD.POSTPARSE_@ ::= AAAA
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

