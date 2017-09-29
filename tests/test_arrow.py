import arrow
import induce
import collections
import random
random.seed(0)


def test_arrow1():
    lines = '''
2013-05-11T21:23:58.970460+00:00
2013-05-07T04:20:39.369271+00:00
2013-05-07T04:24:24.152325+00:00
2013-05-05T00:00:00-07:00
2013-05-06T21:24:49.552236-07:00
1980-05-01T00:00:00+00:00
'''[1:-1]
    grammar = '''
$START ::= $_PARSE_MULTIFORMAT:STRING
$_PARSE_MULTIFORMAT:STRING ::= $PARSE_ISO:DATE_STRINGT$PARSE_ISO:TIME_STRING
$PARSE_ISO:DATE_STRING ::= $_PARSE_TOKEN:VALUE-$_PARSE_TOKEN:VALUE-$_PARSE_TOKEN:VALUE
$PARSE_ISO:TIME_STRING ::= $_PARSE_TOKEN:VALUE:$_PARSE_TOKEN:VALUE:$_PARSE_TOKEN:VALUE+$_PARSE_TOKEN:VALUE:$_PARSE_TOKEN:VALUE
	| $_PARSE_TOKEN:VALUE:$_PARSE_TOKEN:VALUE:$_PARSE_TOKEN:VALUE-$PARSE:HOURS:$_PARSE_TOKEN:VALUE
	| $_PARSE_TOKEN:VALUE:$_PARSE_TOKEN:VALUE:$_PARSE_TOKEN:VALUE.$_PARSE_TOKEN:VALUE$_PARSE_TOKEN:VALUE
$_PARSE_TOKEN:VALUE ::= $PARSE:MINUTES
	| $PARSE:VALUE
	| +$PARSE:MINUTES:$PARSE:MINUTES
	| -$PARSE:HOURS:$PARSE:MINUTES
$PARSE:MINUTES ::= $PARSE:HOURS
	| 00
$PARSE:VALUE ::= 01
	| 04
	| 05
	| 06
	| 07
	| 11
	| 152325
	| 1980
	| 20
	| 2013
	| 21
	| 23
	| 24
	| 369271
	| 39
	| 49
	| 552236
	| 58
	| 970460
$PARSE:HOURS ::= 00
	| 07
'''[1:-1]
    result = []
    for line in lines.split('\n'):
        with induce.Tracer(line, result) as t:
            arrow.get(line)

    with induce.grammar() as g:
        for jframe in result:
            g.handle_events(jframe)
        print(str(g))
        assert(grammar == str(g))
