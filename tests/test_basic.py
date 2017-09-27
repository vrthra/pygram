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
            if len(jframe) == 0:
                g.reset()
            else:
                g.update(jframe)
        grammar = str(g)
    return(parts, out, grammar)

def test_basic1():
    data = '''
CS 2110
'''[1:-1]
    result = [[('CS', '2110')]]
    grammar = '''
$START ::= $ASTR
$ASTR ::= $DEPT $TOK
$TOK ::= $NUMBER
$DEPT ::= CS
$NUMBER ::= 2110
'''[1:-1]
    parts, out, g = helper(data)
    assert(parts == result)
    assert(len(out) == 26)
    assert(grammar == g)


def test_basic2():
    data = '''
CS 2110 and INFO 3300
'''[1:-1]
    result = [[('CS', '2110'), ('INFO', '3300')]]
    grammar = '''
$START ::= $ASTR
$ASTR ::= CS 2110 and $DEPT $TOK
$TOK ::= $NUMBER
$DEPT ::= INFO
$NUMBER ::= 3300
'''[1:-1]
    parts, out, g = helper(data)
    assert(parts == result)
    assert(len(out) == 38)
    assert(grammar == g)


def test_basic3():
    data = '''
CS 2110, INFO 3300
'''[1:-1]
    result = [[('CS', '2110'), ('INFO', '3300')]]
    grammar = '''
$START ::= $ASTR
$ASTR ::= CS 2110, $DEPT $TOK
$TOK ::= $NUMBER
$DEPT ::= INFO
$NUMBER ::= 3300
'''[1:-1]
    parts, out, g = helper(data)
    assert(parts == result)
    assert(len(out) == 38)
    assert(grammar == g)


def test_basic4():
    data = '''
CS 2110, 3300, 3140
'''[1:-1]
    result = [[('CS', '2110'), ('CS', '3300'), ('CS', '3140')]]
    grammar = '''
$START ::= $ASTR
$ASTR ::= $DEPT 2110, 3300, $TOK
$TOK ::= $NUMBER
$DEPT ::= CS
$NUMBER ::= 3140
'''[1:-1]
    parts, out, g = helper(data)
    assert(parts == result)
    assert(len(out) == 38)
    assert(grammar == g)


def test_basic5():
    data = '''
CS 2110 or INFO 3300
'''[1:-1]
    result = [[('CS', '2110')], [('INFO', '3300')]]
    grammar = '''
$START ::= $ASTR
$ASTR ::= CS 2110 or $DEPT $TOK
$TOK ::= $NUMBER
$DEPT ::= INFO
$NUMBER ::= 3300
'''[1:-1]
    parts, out, g = helper(data)
    assert(parts == result)
    assert(len(out) == 43)
    assert(grammar == g)

def test_basic6():
    data = '''
MATH 2210, 2230, 2310, or 2940
'''[1:-1]
    result =   [[('MATH', '2210'), ('MATH', '2230'), ('MATH', '2310')], [('MATH', '2940')]]
    grammar = '''
$START ::= $ASTR
$ASTR ::= $DEPT 2210, 2230, 2310, or $TOK
$TOK ::= $NUMBER
$DEPT ::= MATH
$NUMBER ::= 2940
'''[1:-1]
    parts, out, g = helper(data)
    assert(parts == result)
    assert(len(out) == 49)
    assert(grammar == g)

def test_basic_full():
    data = '''
CS 2110
CS 2110 and INFO 3300
CS 2110, INFO 3300
CS 2110, 3300, 3140
CS 2110 or INFO 3300
MATH 2210, 2230, 2310, or 2940
'''[1:-1]
    grammar = '''
$START ::= $ASTR
$ASTR ::= $DEPT $TOK
	| CS 2110 and $DEPT $TOK
	| CS 2110, $DEPT $TOK
	| $DEPT 2110, 3300, $TOK
	| CS 2110 or $DEPT $TOK
	| $DEPT 2210, 2230, 2310, or $TOK
$TOK ::= $NUMBER
$DEPT ::= CS
	| INFO
	| MATH
$NUMBER ::= 2110
	| 3300
	| 3140
	| 2940
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
            if len(jframe) == 0:
                g.reset()
            else:
                g.update(jframe)
        gout = str(g)
    assert(grammar == gout)


