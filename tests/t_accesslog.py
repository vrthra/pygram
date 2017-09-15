import unittest
import accesslog
import induce, helpers


myinput ='''\
1.1.1.1 - - [21/Feb/2014:06:35:45 +0100] "GET /robots.txt HTTP/1.1" 200 112 "-" "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
'''

mygrammar='''\
$STRING ::= $IP - - [21/Feb/2014:06:35:45 +0100] "$REQUEST" 200 112 "-" "$USERAGENT"
$IP ::= 1.1.1.1
$START ::= $STRING

$USERAGENT ::= Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)
$REQUEST ::= GET /robots.txt HTTP/1.1\
'''


class TestAccesslog(unittest.TestCase):
    def test_induce(self):
        with induce.grammar(True) as g:
           summary = accesslog.LogAnalyzer(myinput, 5)
           with induce.Tracer(myinput, g):
              summary.analyze()
        val = "%s" % g
        self.assertEqual(val, mygrammar)


if __name__ == '__main__':
    unittest.main()
