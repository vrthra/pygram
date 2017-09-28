from datetime import datetime
import induce
import collections
import random
random.seed(0)


def test_dateparse1():
    date_lines = '''
Jun 1 2005  1:33PM|%b %d %Y %I:%M%p
'''[1:-1]
    grammar = '''
$START ::= $_STRPTIME_DATETIME:DATA_STRING|$_STRPTIME_DATETIME:FORMAT
$_STRPTIME_DATETIME:DATA_STRING ::= $<LISTCOMP>:__GETITEM___@ 1 $FOUND_DICT.Y  1:$FOUND_DICT.M$FOUND_DICT.P
$_STRPTIME_DATETIME:FORMAT ::= $_STRPTIME:FORMAT
$<LISTCOMP>:__GETITEM___@ ::= $FOUND_DICT.B
$_STRPTIME:FORMAT ::= $COMPILE:FORMAT
$FOUND_DICT.M ::= 33
$FOUND_DICT.Y ::= 2005
$FOUND_DICT.P ::= PM
$COMPILE:FORMAT ::= $PATTERN:FORMAT
$FOUND_DICT.B ::= Jun
$PATTERN:FORMAT ::= $<LAMBDA>:X %d %Y %I:%M%p
$<LAMBDA>:X ::= $_LOCALIZED_MONTH.FORMAT
$_LOCALIZED_MONTH.FORMAT ::= %b
'''[1:-1]
    result = []
    for line in date_lines.split('\n'):
        if line.strip() == '': continue
        dat, fmt = line.split('|')
        with induce.Tracer(line, result) as t:
            datetime.strptime(dat, fmt)

    with induce.grammar() as g:
        for jframe in result:
            g.handle_events(jframe)
        print(str(g))
        assert(grammar == str(g))

def test_dateparse2():
    date_lines = '''
Jun 1 2005  1:33PM|%b %d %Y %I:%M%p
Aug 28 1999 12:00AM|%b %d %Y %I:%M%p
Jun 1 2005  1:33PM|%b %d %Y %I:%M%p
1 Dec 00|%d %b %y
2 Nov 01|%d %b %y
3 Oct 02|%d %b %y
4 Sep 03|%d %b %y
13 Nov 90|%d %b %y
14 Oct 10|%d %b %y
'''[1:-1]
    grammar = '''
$START ::= $_STRPTIME_DATETIME:DATA_STRING|$_STRPTIME_DATETIME:FORMAT
$_STRPTIME_DATETIME:DATA_STRING ::= $_STRPTIME:DATA_STRING
$_STRPTIME_DATETIME:FORMAT ::= $_STRPTIME:FORMAT
$_STRPTIME:DATA_STRING ::= $ARG
$_STRPTIME:FORMAT ::= $ARG
	| $COMPILE:FORMAT
$ARG ::= $FOUND_DICT.B $FOUND_DICT.D $FOUND_DICT.Y $FOUND_DICT.I:$FOUND_DICT.M$FOUND_DICT.P
	| $FOUND_DICT.B 1 $FOUND_DICT.Y  1:$FOUND_DICT.M$FOUND_DICT.P
	| $FOUND_DICT.D $FOUND_DICT.B $FOUND_DICT.Y
	| %b %d %Y %I:%M%p
	| %d %b %y
	| 1 $FOUND_DICT.B $FOUND_DICT.Y
	| 2 $FOUND_DICT.B $FOUND_DICT.Y
	| 3 $FOUND_DICT.B $FOUND_DICT.Y
	| 4 $FOUND_DICT.B $FOUND_DICT.Y
$FOUND_DICT.M ::= 00
	| 33
$FOUND_DICT.Y ::= 00
	| 01
	| 02
	| 03
	| 10
	| 1999
	| 2005
	| 90
$FOUND_DICT.B ::= Aug
	| Dec
	| Jun
	| Nov
	| Oct
	| Sep
$FOUND_DICT.P ::= AM
	| PM
$FOUND_DICT.I ::= 12
$FOUND_DICT.D ::= 13
	| 14
	| 28
$COMPILE:FORMAT ::= $PATTERN:FORMAT
$PATTERN:FORMAT ::= %d %b %y
'''[1:-1]
    result = []
    for line in date_lines.split('\n'):
        if line.strip() == '': continue
        dat, fmt = line.split('|')
        with induce.Tracer(line, result) as t:
            datetime.strptime(dat, fmt)

    with induce.grammar() as g:
        for jframe in result:
            g.handle_events(jframe)
        print(str(g))
        assert(grammar == str(g))
