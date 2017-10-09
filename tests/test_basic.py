import induce
import collections

def basic_parse(astr):
    astr=astr.replace(',','')
    astr=astr.replace('and','')
    tokens=astr.split()
    dept=None
    number=None
    result=[]
    option=[]
    for tok in tokens:
        if tok=='or':
            result.append(option)
            option=[]
            continue
        if tok.isalpha():
            dept=tok
            number=None
        else:
            number=tok
        if dept and number:
            option.append((dept,number))
    else:
        if option:
            result.append(option)
    return result

def helper(data):
    out = []
    parts = None
    grammar = None
    with induce.Tracer(data, out) as t:
        parts = basic_parse(data)
    with induce.grammar(True) as g:
        for jframe in out:
            g.handle_events(jframe)
        grammar = str(g)
    return(parts, out, grammar)

def test_basic1():
    data = '''
CS 2110
'''[1:-1]
    result = [[('CS', '2110')]]
    grammar = '''
$START ::= $@.BASIC_PARSE:DEPT $@.BASIC_PARSE:NUMBER
$@.BASIC_PARSE:NUMBER ::= $@.BASIC_PARSE:TOK
$@.BASIC_PARSE:DEPT ::= $@.BASIC_PARSE:TOK
$@.BASIC_PARSE:TOK ::= 2110
	| CS
'''[1:-1]
    parts, out, g = helper(data)
    print(g)
    assert(grammar == g)


def test_basic2():
    data = '''
CS 2110 and INFO 3300
'''[1:-1]
    result = [[('CS', '2110'), ('INFO', '3300')]]
    grammar = '''
$START ::= $@.BASIC_PARSE:DEPT $@.BASIC_PARSE:NUMBER and $@.BASIC_PARSE:DEPT $@.BASIC_PARSE:NUMBER
$@.BASIC_PARSE:NUMBER ::= $@.BASIC_PARSE:TOK
$@.BASIC_PARSE:DEPT ::= $@.BASIC_PARSE:TOK
$@.BASIC_PARSE:TOK ::= 2110
	| 3300
	| CS
	| INFO
'''[1:-1]
    parts, out, g = helper(data)
    print(g)
    assert(grammar == g)


def test_basic3():
    data = '''
CS 2110, INFO 3300
'''[1:-1]
    result = [[('CS', '2110'), ('INFO', '3300')]]
    grammar = '''
$START ::= $@.BASIC_PARSE:DEPT $@.BASIC_PARSE:NUMBER, $@.BASIC_PARSE:DEPT $@.BASIC_PARSE:NUMBER
$@.BASIC_PARSE:NUMBER ::= $@.BASIC_PARSE:TOK
$@.BASIC_PARSE:DEPT ::= $@.BASIC_PARSE:TOK
$@.BASIC_PARSE:TOK ::= 2110
	| 3300
	| CS
	| INFO
'''[1:-1]
    parts, out, g = helper(data)
    print(g)
    assert(grammar == g)


def test_basic4():
    data = '''
CS 2110, 3300, 3140
'''[1:-1]
    result = [[('CS', '2110'), ('CS', '3300'), ('CS', '3140')]]
    grammar = '''
$START ::= $@.BASIC_PARSE:DEPT $@.BASIC_PARSE:NUMBER, $@.BASIC_PARSE:NUMBER, $@.BASIC_PARSE:NUMBER
$@.BASIC_PARSE:NUMBER ::= $@.BASIC_PARSE:TOK
$@.BASIC_PARSE:DEPT ::= $@.BASIC_PARSE:TOK
$@.BASIC_PARSE:TOK ::= 2110
	| 3140
	| 3300
	| CS
'''[1:-1]
    parts, out, g = helper(data)
    print(g)
    assert(grammar == g)


def test_basic5():
    data = '''
CS 2110 or INFO 3300
'''[1:-1]
    result = [[('CS', '2110')], [('INFO', '3300')]]
    grammar = '''
$START ::= $@.BASIC_PARSE:DEPT $@.BASIC_PARSE:NUMBER $@.BASIC_PARSE:TOK $@.BASIC_PARSE:DEPT $@.BASIC_PARSE:NUMBER
$@.BASIC_PARSE:NUMBER ::= 2110
	| 3300
$@.BASIC_PARSE:DEPT ::= CS
	| INFO
$@.BASIC_PARSE:TOK ::= or
'''[1:-1]
    parts, out, g = helper(data)
    print(g)
    assert(grammar == g)

def test_basic6():
    data = '''
MATH 2210, 2230, 2310, or 2940
'''[1:-1]
    result =   [[('MATH', '2210'), ('MATH', '2230'), ('MATH', '2310')], [('MATH', '2940')]]
    grammar = '''
$START ::= $@.BASIC_PARSE:DEPT $@.BASIC_PARSE:NUMBER, $@.BASIC_PARSE:NUMBER, $@.BASIC_PARSE:NUMBER, $@.BASIC_PARSE:TOK $@.BASIC_PARSE:NUMBER
$@.BASIC_PARSE:NUMBER ::= 2210
	| 2230
	| 2310
	| 2940
$@.BASIC_PARSE:DEPT ::= MATH
$@.BASIC_PARSE:TOK ::= or
'''[1:-1]
    parts, out, g = helper(data)
    print(g)
    assert(grammar == g)

def test_basic7():
    data = '''
CS 2110
CS 2110 and INFO 3300
CS 2110, INFO 3300
CS 2110, 3300, 3140
CS 2110 or INFO 3300
MATH 2210, 2230, 2310, or 2940
'''[1:-1]
    grammar = '''
$START ::= $@.BASIC_PARSE:DEPT $@.BASIC_PARSE:NUMBER
	| $@.BASIC_PARSE:DEPT $@.BASIC_PARSE:NUMBER $@.BASIC_PARSE:TOK $@.BASIC_PARSE:DEPT $@.BASIC_PARSE:NUMBER
	| $@.BASIC_PARSE:DEPT $@.BASIC_PARSE:NUMBER and $@.BASIC_PARSE:DEPT $@.BASIC_PARSE:NUMBER
	| $@.BASIC_PARSE:DEPT $@.BASIC_PARSE:NUMBER, $@.BASIC_PARSE:DEPT $@.BASIC_PARSE:NUMBER
	| $@.BASIC_PARSE:DEPT $@.BASIC_PARSE:NUMBER, $@.BASIC_PARSE:NUMBER, $@.BASIC_PARSE:NUMBER
	| $@.BASIC_PARSE:DEPT $@.BASIC_PARSE:NUMBER, $@.BASIC_PARSE:NUMBER, $@.BASIC_PARSE:NUMBER, $@.BASIC_PARSE:TOK $@.BASIC_PARSE:NUMBER
$@.BASIC_PARSE:NUMBER ::= $@.BASIC_PARSE:TOK
	| 2110
	| 2210
	| 2230
	| 2310
	| 2940
	| 3300
$@.BASIC_PARSE:DEPT ::= $@.BASIC_PARSE:TOK
	| CS
	| INFO
	| MATH
$@.BASIC_PARSE:TOK ::= 2110
	| 3140
	| 3300
	| CS
	| INFO
	| or
'''[1:-1]
    out = []
    parts = None
    gout = None
    ldata = data.split('\n')
    for l in ldata:
        with induce.Tracer(l, out) as t:
            parts = basic_parse(l)
    with induce.grammar(True) as g:
        for jframe in out:
            g.handle_events(jframe)
        gout = str(g)
    print(gout)
    assert(grammar == gout)


