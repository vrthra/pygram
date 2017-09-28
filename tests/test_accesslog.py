from urllib.parse import urlparse
import induce
import collections
import random
import accesslog
random.seed(0)


def test_accesslog1():
    content_lines = '''
1.1.1.1 - - [21/Feb/2014:06:35:45 +0100] "GET /robots.txt HTTP/1.1" 200 112 "-" "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
'''[1:-1]
    grammar = '''
$START ::= $ANALYZE:IP - - [21/Feb/2014:06:35:45 +0100] "$ANALYZE:REQUEST" 200 112 "-" "$ANALYZE:USERAGENT"
$ANALYZE:USERAGENT ::= $SUMMARIZE:COL.USERAGENT
$ANALYZE:REQUEST ::= $SUMMARIZE:COL.REQUEST
$ANALYZE:IP ::= $SUMMARIZE:COL.IP
$SUMMARIZE:COL.USERAGENT ::= Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)
$SUMMARIZE:COL.REQUEST ::= GET /robots.txt HTTP/1.1
$SUMMARIZE:COL.IP ::= 1.1.1.1
'''[1:-1]
    result = []
    for line in content_lines.split('\n'):
        with induce.Tracer(line, result) as t:
            summary = accesslog.LogAnalyzer(line, 5)
            summary.analyze()

    with induce.grammar() as g:
        for jframe in result: g.handle_events(jframe)
        print(str(g))
        assert(grammar == str(g))

def test_accesslog2():
    content_lines = '''
1.1.1.1 - - [21/Feb/2014:06:35:45 +0100] "GET /robots.txt HTTP/1.1" 200 112 "-" "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
1.1.1.1 - - [21/Feb/2014:06:35:45 +0100] "GET /blog.css HTTP/1.1" 200 3663 "-" "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
2.2.2.2 - - [21/Feb/2014:06:52:04 +0100] "GET /main/rss HTTP/1.1" 301 178 "-" "Motorola"
2.2.2.2 - - [21/Feb/2014:06:52:04 +0100] "GET /feed/atom.xml HTTP/1.1" 304 0 "-" "Motorola"
3.3.3.3 - - [21/Feb/2014:06:58:14 +0100] "/" 200 1664 "-" "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.117"
4.4.4.4 - - [21/Feb/2014:07:22:03 +0100] "/" 200 1664 "-" "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.117"
5.5.5.5 - - [21/Feb/2014:07:32:48 +0100] "GET /main/rss HTTP/1.1" 301 178 "-" "Motorola"
5.5.5.5 - - [21/Feb/2014:07:32:48 +0100] "GET /feed/atom.xml HTTP/1.1" 304 0 "-" "Motorola"
6.6.6.6 - - [21/Feb/2014:08:13:01 +0100] "GET /main/rss HTTP/1.1" 301 178 "-" "Motorola"
6.6.6.6 - - [21/Feb/2014:08:13:01 +0100] "GET /feed/atom.xml HTTP/1.1" 304 0 "-" "Motorola"
7.7.7.7 - - [21/Feb/2014:08:51:25 +0100] "GET /main.php HTTP/1.1" 200 3681 "-" "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; Q312461)"
7.7.7.7 - - [21/Feb/2014:08:51:34 +0100] "-" 400 0 "-" "-"
7.7.7.7 - - [21/Feb/2014:08:51:48 +0100] "GET /tag/php.php HTTP/1.1" 200 4673 "-" "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; Q312461)"
8.8.8.8 - - [21/Feb/2014:08:53:43 +0100] "GET /main/rss HTTP/1.1" 301 178 "-" "Motorola"
8.8.8.8 - - [21/Feb/2014:08:53:43 +0100] "GET /feed/atom.xml HTTP/1.1" 304 0 "-" "Motorola"
9.9.9.9 - - [21/Feb/2014:09:18:40 +0100] "-" 400 0 "-" "-"
9.9.9.9 - - [21/Feb/2014:09:18:40 +0100] "GET /main HTTP/1.1" 200 3681 "-" "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.117"
9.9.9.9 - - [21/Feb/2014:09:18:41 +0100] "GET /phpMyAdmin/scripts/setup.php HTTP/1.1" 404 27 "-" "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.117"
9.9.9.9 - - [21/Feb/2014:09:18:42 +0100] "GET /pma/scripts/setup.php HTTP/1.1" 404 27 "-" "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.117"
10.10.10.10 - - [21/Feb/2014:09:21:29 +0100] "-" 400 0 "-" "-"
10.10.10.10 - - [21/Feb/2014:09:21:29 +0100] "GET /main.php HTTP/1.1" 200 3681 "-" "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.117"
10.10.10.10 - - [21/Feb/2014:09:21:30 +0100] "GET /about.php HTTP/1.1" 200 2832 "-" "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.117"
10.10.10.10 - - [21/Feb/2014:09:21:30 +0100] "GET /tag/nginx.php HTTP/1.1" 200 3295 "-" "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.117"
10.10.10.10 - - [21/Feb/2014:09:21:31 +0100] "GET /how-to-setup.php HTTP/1.1" 200 2637 "-" "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.117"
1.1.1.1 - - [21/Feb/2014:09:27:27 +0100] "GET /robots.txt HTTP/1.1" 200 112 "-" "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
1.1.1.1 - - [21/Feb/2014:09:27:27 +0100] "GET /tag/tor.php HTTP/1.1" 200 2041 "-" "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
5.5.5.5 - - [21/Feb/2014:10:14:37 +0100] "GET /main/rss HTTP/1.1" 301 178 "-" "Motorola"
5.5.5.5 - - [21/Feb/2014:10:14:37 +0100] "GET /feed/atom.xml HTTP/1.1" 304 0 "-" "Motorola"
8.8.8.8 - - [21/Feb/2014:10:55:19 +0100] "GET /main/rss HTTP/1.1" 301 178 "-" "Motorola"
8.8.8.8 - - [21/Feb/2014:10:55:19 +0100] "GET /feed/atom.xml HTTP/1.1" 304 0 "-" "Motorola"
1.1.1.1 - - [21/Feb/2014:11:19:05 +0100] "GET /robots.txt HTTP/1.1" 200 112 "-" "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
1.1.1.1 - - [21/Feb/2014:11:19:06 +0100] "GET /robots.txt HTTP/1.1" 200 112 "-" "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
1.1.1.1 - - [21/Feb/2014:11:19:06 +0100] "GET / HTTP/1.1" 200 3649 "-" "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
6.6.6.6 - - [21/Feb/2014:12:16:14 +0100] "GET /main/rss HTTP/1.1" 301 178 "-" "Motorola"
6.6.6.6 - - [21/Feb/2014:12:16:15 +0100] "GET /feed/atom.xml HTTP/1.1" 304 0 "-" "Motorola"
5.5.5.5 - - [21/Feb/2014:14:17:52 +0100] "GET /main/rss HTTP/1.1" 301 178 "-" "Motorola"
5.5.5.5 - - [21/Feb/2014:14:17:52 +0100] "GET /feed/atom.xml HTTP/1.1" 304 0 "-" "Motorola"
6.6.6.6 - - [21/Feb/2014:14:58:04 +0100] "GET /main/rss HTTP/1.1" 301 178 "-" "Motorola"
6.6.6.6 - - [21/Feb/2014:14:58:04 +0100] "GET /feed/atom.xml HTTP/1.1" 304 0 "-" "Motorola"
5.5.5.5 - - [21/Feb/2014:15:38:46 +0100] "GET /main/rss HTTP/1.1" 301 178 "-" "Motorola"
5.5.5.5 - - [21/Feb/2014:15:38:47 +0100] "GET /feed/atom.xml HTTP/1.1" 304 0 "-" "Motorola"
2.2.2.2 - - [21/Feb/2014:18:20:36 +0100] "GET /main/rss HTTP/1.1" 301 178 "-" "Motorola"
2.2.2.2 - - [21/Feb/2014:18:20:37 +0100] "GET /feed/atom.xml HTTP/1.1" 304 0 "-" "Motorola"
5.5.5.5 - - [21/Feb/2014:19:42:00 +0100] "GET /main/rss HTTP/1.1" 301 178 "-" "Motorola"
5.5.5.5 - - [21/Feb/2014:19:42:00 +0100] "GET /feed/atom.xml HTTP/1.1" 304 0 "-" "Motorola"
2.2.2.2 - - [21/Feb/2014:20:22:13 +0100] "GET /main/rss HTTP/1.1" 301 178 "-" "Motorola"
2.2.2.2 - - [21/Feb/2014:20:22:13 +0100] "GET /feed/atom.xml HTTP/1.1" 304 0 "-" "Motorola"
6.6.6.6 - - [21/Feb/2014:21:02:55 +0100] "GET /main/rss HTTP/1.1" 301 178 "-" "Motorola"
6.6.6.6 - - [21/Feb/2014:21:02:55 +0100] "GET /feed/atom.xml HTTP/1.1" 304 0 "-" "Motorola"
8.8.8.8 - - [22/Feb/2014:01:05:37 +0100] "GET /main/rss HTTP/1.1" 301 178 "-" "Motorola"
8.8.8.8 - - [22/Feb/2014:01:05:38 +0100] "GET /feed/atom.xml HTTP/1.1" 304 0 "-" "Motorola"
8.8.8.8 - - [22/Feb/2014:04:28:10 +0100] "GET /main/rss HTTP/1.1" 301 178 "-" "Motorola"
8.8.8.8 - - [22/Feb/2014:04:28:10 +0100] "GET /feed/atom.xml HTTP/1.1" 304 0 "-" "Motorola"
2.2.2.2 - - [22/Feb/2014:05:49:34 +0100] "GET /main/rss HTTP/1.1" 301 178 "-" "Motorola"
2.2.2.2 - - [22/Feb/2014:05:49:34 +0100] "GET /feed/atom.xml HTTP/1.1" 304 0 "-" "Motorola"
5.5.5.5 - - [22/Feb/2014:06:29:47 +0100] "GET /main/rss HTTP/1.1" 301 178 "-" "Motorola"
5.5.5.5 - - [22/Feb/2014:06:29:47 +0100] "GET /feed/atom.xml HTTP/1.1" 304 0 "-" "Motorola"
'''[1:-1]
    grammar = '''
$START ::= $ANALYZE:IP - - [21/Feb/2014:06:35:45 +0100] "$ANALYZE:REQUEST" 200 112 "-" "$ANALYZE:USERAGENT"
	| $ANALYZE:IP - - [21/Feb/2014:06:35:45 +0100] "$ANALYZE:REQUEST" 200 3663 "-" "$ANALYZE:USERAGENT"
	| $ANALYZE:IP - - [21/Feb/2014:06:52:04 +0100] "$ANALYZE:REQUEST" 301 178 "-" "$ANALYZE:USERAGENT"
	| $ANALYZE:IP - - [21/Feb/2014:06:52:04 +0100] "$ANALYZE:REQUEST" 304 0 "-" "$ANALYZE:USERAGENT"
	| $ANALYZE:IP - - [21/Feb/2014:06:58:14 +0100] "/" 200 1664 "-" "$ANALYZE:USERAGENT"
	| $ANALYZE:IP - - [21/Feb/2014:07:22:03 +0100] "/" 200 1664 "-" "$ANALYZE:USERAGENT"
	| $ANALYZE:IP - - [21/Feb/2014:07:32:48 +0100] "$ANALYZE:REQUEST" 301 178 "-" "$ANALYZE:USERAGENT"
	| $ANALYZE:IP - - [21/Feb/2014:07:32:48 +0100] "$ANALYZE:REQUEST" 304 0 "-" "$ANALYZE:USERAGENT"
	| $ANALYZE:IP - - [21/Feb/2014:08:13:01 +0100] "$ANALYZE:REQUEST" 301 178 "-" "$ANALYZE:USERAGENT"
	| $ANALYZE:IP - - [21/Feb/2014:08:13:01 +0100] "$ANALYZE:REQUEST" 304 0 "-" "$ANALYZE:USERAGENT"
	| $ANALYZE:IP - - [21/Feb/2014:08:51:25 +0100] "$ANALYZE:REQUEST" 200 3681 "-" "$ANALYZE:USERAGENT"
	| $ANALYZE:IP - - [21/Feb/2014:08:51:48 +0100] "$ANALYZE:REQUEST" 200 4673 "-" "$ANALYZE:USERAGENT"
	| $ANALYZE:IP - - [21/Feb/2014:08:53:43 +0100] "$ANALYZE:REQUEST" 301 178 "-" "$ANALYZE:USERAGENT"
	| $ANALYZE:IP - - [21/Feb/2014:08:53:43 +0100] "$ANALYZE:REQUEST" 304 0 "-" "$ANALYZE:USERAGENT"
	| $ANALYZE:IP - - [21/Feb/2014:09:18:40 +0100] "$ANALYZE:REQUEST" 200 3681 "-" "$ANALYZE:USERAGENT"
	| $ANALYZE:IP - - [21/Feb/2014:09:18:41 +0100] "$ANALYZE:REQUEST" 404 27 "-" "$ANALYZE:USERAGENT"
	| $ANALYZE:IP - - [21/Feb/2014:09:18:42 +0100] "$ANALYZE:REQUEST" 404 27 "-" "$ANALYZE:USERAGENT"
	| $ANALYZE:IP - - [21/Feb/2014:09:21:29 +0100] "$ANALYZE:REQUEST" 200 3681 "-" "$ANALYZE:USERAGENT"
	| $ANALYZE:IP - - [21/Feb/2014:09:21:30 +0100] "$ANALYZE:REQUEST" 200 2832 "-" "$ANALYZE:USERAGENT"
	| $ANALYZE:IP - - [21/Feb/2014:09:21:30 +0100] "$ANALYZE:REQUEST" 200 3295 "-" "$ANALYZE:USERAGENT"
	| $ANALYZE:IP - - [21/Feb/2014:09:21:31 +0100] "$ANALYZE:REQUEST" 200 2637 "-" "$ANALYZE:USERAGENT"
	| $ANALYZE:IP - - [21/Feb/2014:09:27:27 +0100] "$ANALYZE:REQUEST" 200 112 "-" "$ANALYZE:USERAGENT"
	| $ANALYZE:IP - - [21/Feb/2014:09:27:27 +0100] "$ANALYZE:REQUEST" 200 2041 "-" "$ANALYZE:USERAGENT"
	| $ANALYZE:IP - - [21/Feb/2014:10:14:37 +0100] "$ANALYZE:REQUEST" 301 178 "-" "$ANALYZE:USERAGENT"
	| $ANALYZE:IP - - [21/Feb/2014:10:14:37 +0100] "$ANALYZE:REQUEST" 304 0 "-" "$ANALYZE:USERAGENT"
	| $ANALYZE:IP - - [21/Feb/2014:10:55:19 +0100] "$ANALYZE:REQUEST" 301 178 "-" "$ANALYZE:USERAGENT"
	| $ANALYZE:IP - - [21/Feb/2014:10:55:19 +0100] "$ANALYZE:REQUEST" 304 0 "-" "$ANALYZE:USERAGENT"
	| $ANALYZE:IP - - [21/Feb/2014:11:19:05 +0100] "$ANALYZE:REQUEST" 200 112 "-" "$ANALYZE:USERAGENT"
	| $ANALYZE:IP - - [21/Feb/2014:11:19:06 +0100] "$ANALYZE:REQUEST" 200 112 "-" "$ANALYZE:USERAGENT"
	| $ANALYZE:IP - - [21/Feb/2014:11:19:06 +0100] "$ANALYZE:REQUEST" 200 3649 "-" "$ANALYZE:USERAGENT"
	| $ANALYZE:IP - - [21/Feb/2014:12:16:14 +0100] "$ANALYZE:REQUEST" 301 178 "-" "$ANALYZE:USERAGENT"
	| $ANALYZE:IP - - [21/Feb/2014:12:16:15 +0100] "$ANALYZE:REQUEST" 304 0 "-" "$ANALYZE:USERAGENT"
	| $ANALYZE:IP - - [21/Feb/2014:14:17:52 +0100] "$ANALYZE:REQUEST" 301 178 "-" "$ANALYZE:USERAGENT"
	| $ANALYZE:IP - - [21/Feb/2014:14:17:52 +0100] "$ANALYZE:REQUEST" 304 0 "-" "$ANALYZE:USERAGENT"
	| $ANALYZE:IP - - [21/Feb/2014:14:58:04 +0100] "$ANALYZE:REQUEST" 301 178 "-" "$ANALYZE:USERAGENT"
	| $ANALYZE:IP - - [21/Feb/2014:14:58:04 +0100] "$ANALYZE:REQUEST" 304 0 "-" "$ANALYZE:USERAGENT"
	| $ANALYZE:IP - - [21/Feb/2014:15:38:46 +0100] "$ANALYZE:REQUEST" 301 178 "-" "$ANALYZE:USERAGENT"
	| $ANALYZE:IP - - [21/Feb/2014:15:38:47 +0100] "$ANALYZE:REQUEST" 304 0 "-" "$ANALYZE:USERAGENT"
	| $ANALYZE:IP - - [21/Feb/2014:18:20:36 +0100] "$ANALYZE:REQUEST" 301 178 "-" "$ANALYZE:USERAGENT"
	| $ANALYZE:IP - - [21/Feb/2014:18:20:37 +0100] "$ANALYZE:REQUEST" 304 0 "-" "$ANALYZE:USERAGENT"
	| $ANALYZE:IP - - [21/Feb/2014:19:42:00 +0100] "$ANALYZE:REQUEST" 301 178 "-" "$ANALYZE:USERAGENT"
	| $ANALYZE:IP - - [21/Feb/2014:19:42:00 +0100] "$ANALYZE:REQUEST" 304 0 "-" "$ANALYZE:USERAGENT"
	| $ANALYZE:IP - - [21/Feb/2014:20:22:13 +0100] "$ANALYZE:REQUEST" 301 178 "-" "$ANALYZE:USERAGENT"
	| $ANALYZE:IP - - [21/Feb/2014:20:22:13 +0100] "$ANALYZE:REQUEST" 304 0 "-" "$ANALYZE:USERAGENT"
	| $ANALYZE:IP - - [21/Feb/2014:21:02:55 +0100] "$ANALYZE:REQUEST" 301 178 "-" "$ANALYZE:USERAGENT"
	| $ANALYZE:IP - - [21/Feb/2014:21:02:55 +0100] "$ANALYZE:REQUEST" 304 0 "-" "$ANALYZE:USERAGENT"
	| $ANALYZE:IP - - [22/Feb/2014:01:05:37 +0100] "$ANALYZE:REQUEST" 301 178 "-" "$ANALYZE:USERAGENT"
	| $ANALYZE:IP - - [22/Feb/2014:01:05:38 +0100] "$ANALYZE:REQUEST" 304 0 "-" "$ANALYZE:USERAGENT"
	| $ANALYZE:IP - - [22/Feb/2014:04:28:10 +0100] "$ANALYZE:REQUEST" 301 178 "-" "$ANALYZE:USERAGENT"
	| $ANALYZE:IP - - [22/Feb/2014:04:28:10 +0100] "$ANALYZE:REQUEST" 304 0 "-" "$ANALYZE:USERAGENT"
	| $ANALYZE:IP - - [22/Feb/2014:05:49:34 +0100] "$ANALYZE:REQUEST" 301 178 "-" "$ANALYZE:USERAGENT"
	| $ANALYZE:IP - - [22/Feb/2014:05:49:34 +0100] "$ANALYZE:REQUEST" 304 0 "-" "$ANALYZE:USERAGENT"
	| $ANALYZE:IP - - [22/Feb/2014:06:29:47 +0100] "$ANALYZE:REQUEST" 301 178 "-" "$ANALYZE:USERAGENT"
	| $ANALYZE:IP - - [22/Feb/2014:06:29:47 +0100] "$ANALYZE:REQUEST" 304 0 "-" "$ANALYZE:USERAGENT"
	| $FIND_CHARS:STRING
$ANALYZE:USERAGENT ::= $SUMMARIZE:COL.USERAGENT
$ANALYZE:REQUEST ::= $SUMMARIZE:COL.REQUEST
$ANALYZE:IP ::= $SUMMARIZE:COL.IP
$SUMMARIZE:COL.USERAGENT ::= Motorola
	| Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; Q312461)
	| Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.117
	| Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)
$SUMMARIZE:COL.REQUEST ::= GET / HTTP/1.1
	| GET /about.php HTTP/1.1
	| GET /blog.css HTTP/1.1
	| GET /feed/atom.xml HTTP/1.1
	| GET /how-to-setup.php HTTP/1.1
	| GET /main HTTP/1.1
	| GET /main.php HTTP/1.1
	| GET /main/rss HTTP/1.1
	| GET /phpMyAdmin/scripts/setup.php HTTP/1.1
	| GET /pma/scripts/setup.php HTTP/1.1
	| GET /robots.txt HTTP/1.1
	| GET /tag/nginx.php HTTP/1.1
	| GET /tag/php.php HTTP/1.1
	| GET /tag/tor.php HTTP/1.1
$SUMMARIZE:COL.IP ::= 1.1.1.1
	| 10.10.10.10
	| 2.2.2.2
	| 3.3.3.3
	| 4.4.4.4
	| 5.5.5.5
	| 6.6.6.6
	| 7.7.7.7
	| 8.8.8.8
	| 9.9.9.9
$FIND_CHARS:STRING ::= $__INIT__:CONTENT
$__INIT__:CONTENT ::= $ANALYZE:LINE
$ANALYZE:LINE ::= $ANALYZE:IP - - [21/Feb/2014:08:51:34 +0100] "-" 400 0 "-" "-"
	| $ANALYZE:IP - - [21/Feb/2014:09:18:40 +0100] "-" 400 0 "-" "-"
	| $ANALYZE:IP - - [21/Feb/2014:09:21:29 +0100] "-" 400 0 "-" "-"
'''[1:-1]
    result = []
    for line in content_lines.split('\n'):
        with induce.Tracer(line, result) as t:
            summary = accesslog.LogAnalyzer(line, 5)
            summary.analyze()

    with induce.grammar() as g:
        for jframe in result: g.handle_events(jframe)
        print(str(g))
        assert(grammar == str(g))

