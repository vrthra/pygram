import unittest
import apache_log_parser
from pprint import pprint
import induce, helpers


myinput ='''\
127.0.0.1 <<6113>> [16/Aug/2013:15:45:34 +0000] 1966093us "GET / HTTP/1.1" 200 3478  "https://example.com/" "Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.9.2.18)" - -
'''

mygrammar = '''\
$START ::= $LOG_LINE
$LOG_LINE ::= 127.0.0.1 <<6113>> [16/Aug/2013:15:45:34 $STRING] 1966093us "$FIRST_LINE" 200 3478  "$NAMEs://example.com/" "$UA" - -

$UA ::= $USER_AGENT_STRING
$FIRST_LINE ::= GET / HTTP/1.1
$STRING ::= $TZ_STRING
$NAME ::= http
$USER_AGENT_STRING ::= Mozilla/5.0 (X11; U; $OS x86_64; en-US; rv:1.9.2.18)
$TZ_STRING ::= +0000
$OS ::= $FAMILY
$FAMILY ::= L$OPux
$OP ::= in\
'''

mygrammar = '''\
$START ::= $PARSE:LOG_LINE
$PARSE:LOG_LINE ::= 127.0.0.1 <<6113>> $FORMAT_TIME:TIME_RECEIVED 1966093us "$EXTRA_REQUEST_FROM_FIRST_LINE:FIRST_LINE" 200 3478  "$_PARSE:NAMEs://example.com/" "$PARSE_USER_AGENT:UA" - -

$PARSE_USER_AGENT:UA ::= $PARSE:USER_AGENT_STRING
$EXTRA_REQUEST_FROM_FIRST_LINE:FIRST_LINE ::= $MATCH:STRING
$_PARSE:NAME ::= http
$FORMAT_TIME:TIME_RECEIVED ::= $APACHETIME:S
$PARSE:USER_AGENT_STRING ::= $PARSEUSERAGENT:USER_AGENT_STRING
$MATCH:STRING ::= GET / HTTP/1.1
$APACHETIME:S ::= [16/Aug/2013:15:45:34 $APACHETIME:TZ_STRING]
$__INIT__:USER_AGENT_STRING ::= $PARSE:USER_AGENT_STRING
$APACHETIME:TZ_STRING ::= $__INIT__:STRING
$__INIT__:STRING ::= +0000
$PARSEUSERAGENT:USER_AGENT_STRING ::= $PARSEOS:USER_AGENT_STRING
$PARSEOS:USER_AGENT_STRING ::= Mozilla/5.0 (X11; U; $PARSE:OS x86_64; en-US; rv:1.9.2.18)
$PARSE:OS ::= $PARSEOS:OS
$PARSEOS:OS ::= $PARSE_OPERATING_SYSTEM:FAMILY
$PARSE_OPERATING_SYSTEM:FAMILY ::= $__NEW__:FAMILY
$__NEW__:FAMILY ::= L$GETWIDTH:OPux
$GETWIDTH:OP ::= $_COMPILE:OP
$_COMPILE:OP ::= in\
'''

# TODO: Here, Linux is substituted by L$OPux.

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

