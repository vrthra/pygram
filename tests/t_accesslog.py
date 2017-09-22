import accesslog
import induce


myinput ='''\
1.1.1.1 - - [21/Feb/2014:06:35:45 +0100] "GET /robots.txt HTTP/1.1" 200 112 "-" "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
'''

mygrammar_d='''\
$START ::= $ANALYZE:S

$ANALYZE:S ::= $ANALYZE:LINE
$ANALYZE:LINE ::= $ANALYZE:IP - - [21/Feb/2014:06:35:45 +0100] "$ANALYZE:REQUEST" 200 112 "-" "$ANALYZE:USERAGENT"
$ANALYZE:IP ::= 1.1.1.1
$ANALYZE:REQUEST ::= GET /robots.txt HTTP/1.1
$ANALYZE:USERAGENT ::= Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)\
'''

summary = accesslog.LogAnalyzer(myinput, 5)
with induce.Tracer():
    summary.analyze()
