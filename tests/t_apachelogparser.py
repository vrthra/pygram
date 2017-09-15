import unittest
import apache_log_parser
from pprint import pprint
import induce, helpers


myinput ='''\
127.0.0.1 <<6113>> [16/Aug/2013:15:45:34 +0000] 1966093us "GET / HTTP/1.1" 200 3478  "https://example.com/" "Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.9.2.18)" - -
'''

mygrammar='''\
$TZ_STRING ::= +0000
$START ::= 127.0.0.1 <<6113>> [16/Aug/2013:15:45:34 $STRING] 1966093us "$STRING" 200 3478  "$NAMEs://example.com/" "Mozilla/5.0 (X11; U; $FAMILY x86_64; en-US; rv:1.9.2.18)" - -

$STRING ::= $TZ_STRING
	| $FIRST_LINE
$FAMILY ::= $OS
$NAME ::= http
$OS ::= L$OPux
$OP ::= in
$FIRST_LINE ::= GET / HTTP/1.1\
'''


class TestApacheLogParser(unittest.TestCase):
    def test_induce(self):
        with induce.grammar(True) as g:
            line_parser = apache_log_parser.make_parser("%h <<%P>> %t %Dus \"%r\" %>s %b  \"%{Referer}i\" \"%{User-Agent}i\" %l %u")
            with induce.Tracer(myinput, g):
                line_parser(myinput)
        val = "%s" % g
        self.assertEqual(val, mygrammar)

if __name__ == '__main__':
    unittest.main()

