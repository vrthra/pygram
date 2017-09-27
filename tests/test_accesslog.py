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
$COL.IP ::= 1.1.1.1
$COL.REQUEST ::= GET /robots.txt HTTP/1.1
$COL.USERAGENT ::= Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)
$FIND_CHARS:STRING ::= $__INIT__:CONTENT
$IP ::= $COL.IP
$REQUEST ::= $COL.REQUEST
$START ::= $FIND_CHARS:STRING
$USERAGENT ::= $COL.USERAGENT
$__INIT__:CONTENT ::= $IP - - [21/Feb/2014:06:35:45 +0100] "$REQUEST" 200 112 "-" "$USERAGENT"
'''[1:-1]
    result = []
    for line in content_lines.split('\n'):
        with induce.Tracer(line, result) as t:
            summary = accesslog.LogAnalyzer(line, 5)
            summary.analyze()
    assert(len(result) == 204)

    with induce.grammar() as g:
        for count, jframe in enumerate(result):
            if len(jframe) == 0:
                g.reset()
            else:
                myframe = collections.OrderedDict()
                for k in sorted(jframe.keys()): myframe[k] = jframe[k]
                g.update(myframe)
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
$COL.IP ::= 1.1.1.1
	| 10.10.10.10
	| 2.2.2.2
	| 3.3.3.3
	| 4.4.4.4
	| 5.5.5.5
	| 6.6.6.6
	| 7.7.7.7
	| 8.8.8.8
	| 9.9.9.9
$COL.REQUEST ::= GET / HTTP/1.1
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
$COL.USERAGENT ::= Motorola
	| Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; Q312461)
	| Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.117
	| Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)
$FIND_CHARS:STRING ::= $__INIT__:CONTENT
$IP ::= $COL.IP
$LINE ::= $IP - - [21/Feb/2014:08:51:34 +0100] "-" 400 0 "-" "-"
	| $IP - - [21/Feb/2014:09:18:40 +0100] "-" 400 0 "-" "-"
	| $IP - - [21/Feb/2014:09:21:29 +0100] "-" 400 0 "-" "-"
$REQUEST ::= $COL.REQUEST
$START ::= $FIND_CHARS:STRING
$USERAGENT ::= $COL.USERAGENT
$__INIT__:CONTENT ::= $IP - - [21/Feb/2014:06:35:45 +0100] "$REQUEST" 200 112 "-" "$USERAGENT"
	| $IP - - [21/Feb/2014:06:35:45 +0100] "$REQUEST" 200 3663 "-" "$USERAGENT"
	| $IP - - [21/Feb/2014:06:52:04 +0100] "$REQUEST" 301 178 "-" "$USERAGENT"
	| $IP - - [21/Feb/2014:06:52:04 +0100] "$REQUEST" 304 0 "-" "$USERAGENT"
	| $IP - - [21/Feb/2014:06:58:14 +0100] "/" 200 1664 "-" "$USERAGENT"
	| $IP - - [21/Feb/2014:07:22:03 +0100] "/" 200 1664 "-" "$USERAGENT"
	| $IP - - [21/Feb/2014:07:32:48 +0100] "$REQUEST" 301 178 "-" "$USERAGENT"
	| $IP - - [21/Feb/2014:07:32:48 +0100] "$REQUEST" 304 0 "-" "$USERAGENT"
	| $IP - - [21/Feb/2014:08:13:01 +0100] "$REQUEST" 301 178 "-" "$USERAGENT"
	| $IP - - [21/Feb/2014:08:13:01 +0100] "$REQUEST" 304 0 "-" "$USERAGENT"
	| $IP - - [21/Feb/2014:08:51:25 +0100] "$REQUEST" 200 3681 "-" "$USERAGENT"
	| $IP - - [21/Feb/2014:08:51:48 +0100] "$REQUEST" 200 4673 "-" "$USERAGENT"
	| $IP - - [21/Feb/2014:08:53:43 +0100] "$REQUEST" 301 178 "-" "$USERAGENT"
	| $IP - - [21/Feb/2014:08:53:43 +0100] "$REQUEST" 304 0 "-" "$USERAGENT"
	| $IP - - [21/Feb/2014:09:18:40 +0100] "$REQUEST" 200 3681 "-" "$USERAGENT"
	| $IP - - [21/Feb/2014:09:18:41 +0100] "$REQUEST" 404 27 "-" "$USERAGENT"
	| $IP - - [21/Feb/2014:09:18:42 +0100] "$REQUEST" 404 27 "-" "$USERAGENT"
	| $IP - - [21/Feb/2014:09:21:29 +0100] "$REQUEST" 200 3681 "-" "$USERAGENT"
	| $IP - - [21/Feb/2014:09:21:30 +0100] "$REQUEST" 200 2832 "-" "$USERAGENT"
	| $IP - - [21/Feb/2014:09:21:30 +0100] "$REQUEST" 200 3295 "-" "$USERAGENT"
	| $IP - - [21/Feb/2014:09:21:31 +0100] "$REQUEST" 200 2637 "-" "$USERAGENT"
	| $IP - - [21/Feb/2014:09:27:27 +0100] "$REQUEST" 200 112 "-" "$USERAGENT"
	| $IP - - [21/Feb/2014:09:27:27 +0100] "$REQUEST" 200 2041 "-" "$USERAGENT"
	| $IP - - [21/Feb/2014:10:14:37 +0100] "$REQUEST" 301 178 "-" "$USERAGENT"
	| $IP - - [21/Feb/2014:10:14:37 +0100] "$REQUEST" 304 0 "-" "$USERAGENT"
	| $IP - - [21/Feb/2014:10:55:19 +0100] "$REQUEST" 301 178 "-" "$USERAGENT"
	| $IP - - [21/Feb/2014:10:55:19 +0100] "$REQUEST" 304 0 "-" "$USERAGENT"
	| $IP - - [21/Feb/2014:11:19:05 +0100] "$REQUEST" 200 112 "-" "$USERAGENT"
	| $IP - - [21/Feb/2014:11:19:06 +0100] "$REQUEST" 200 112 "-" "$USERAGENT"
	| $IP - - [21/Feb/2014:11:19:06 +0100] "$REQUEST" 200 3649 "-" "$USERAGENT"
	| $IP - - [21/Feb/2014:12:16:14 +0100] "$REQUEST" 301 178 "-" "$USERAGENT"
	| $IP - - [21/Feb/2014:12:16:15 +0100] "$REQUEST" 304 0 "-" "$USERAGENT"
	| $IP - - [21/Feb/2014:14:17:52 +0100] "$REQUEST" 301 178 "-" "$USERAGENT"
	| $IP - - [21/Feb/2014:14:17:52 +0100] "$REQUEST" 304 0 "-" "$USERAGENT"
	| $IP - - [21/Feb/2014:14:58:04 +0100] "$REQUEST" 301 178 "-" "$USERAGENT"
	| $IP - - [21/Feb/2014:14:58:04 +0100] "$REQUEST" 304 0 "-" "$USERAGENT"
	| $IP - - [21/Feb/2014:15:38:46 +0100] "$REQUEST" 301 178 "-" "$USERAGENT"
	| $IP - - [21/Feb/2014:15:38:47 +0100] "$REQUEST" 304 0 "-" "$USERAGENT"
	| $IP - - [21/Feb/2014:18:20:36 +0100] "$REQUEST" 301 178 "-" "$USERAGENT"
	| $IP - - [21/Feb/2014:18:20:37 +0100] "$REQUEST" 304 0 "-" "$USERAGENT"
	| $IP - - [21/Feb/2014:19:42:00 +0100] "$REQUEST" 301 178 "-" "$USERAGENT"
	| $IP - - [21/Feb/2014:19:42:00 +0100] "$REQUEST" 304 0 "-" "$USERAGENT"
	| $IP - - [21/Feb/2014:20:22:13 +0100] "$REQUEST" 301 178 "-" "$USERAGENT"
	| $IP - - [21/Feb/2014:20:22:13 +0100] "$REQUEST" 304 0 "-" "$USERAGENT"
	| $IP - - [21/Feb/2014:21:02:55 +0100] "$REQUEST" 301 178 "-" "$USERAGENT"
	| $IP - - [21/Feb/2014:21:02:55 +0100] "$REQUEST" 304 0 "-" "$USERAGENT"
	| $IP - - [22/Feb/2014:01:05:37 +0100] "$REQUEST" 301 178 "-" "$USERAGENT"
	| $IP - - [22/Feb/2014:01:05:38 +0100] "$REQUEST" 304 0 "-" "$USERAGENT"
	| $IP - - [22/Feb/2014:04:28:10 +0100] "$REQUEST" 301 178 "-" "$USERAGENT"
	| $IP - - [22/Feb/2014:04:28:10 +0100] "$REQUEST" 304 0 "-" "$USERAGENT"
	| $IP - - [22/Feb/2014:05:49:34 +0100] "$REQUEST" 301 178 "-" "$USERAGENT"
	| $IP - - [22/Feb/2014:05:49:34 +0100] "$REQUEST" 304 0 "-" "$USERAGENT"
	| $IP - - [22/Feb/2014:06:29:47 +0100] "$REQUEST" 301 178 "-" "$USERAGENT"
	| $IP - - [22/Feb/2014:06:29:47 +0100] "$REQUEST" 304 0 "-" "$USERAGENT"
	| $LINE
'''[1:-1]
    result = []
    for line in content_lines.split('\n'):
        with induce.Tracer(line, result) as t:
            summary = accesslog.LogAnalyzer(line, 5)
            summary.analyze()
    assert(len(result) == 9164)

    with induce.grammar() as g:
        for count, jframe in enumerate(result):
            if len(jframe) == 0:
                g.reset()
            else:
                myframe = collections.OrderedDict()
                for k in sorted(jframe.keys()): myframe[k] = jframe[k]
                g.update(myframe)
        print(str(g))
        assert(grammar == str(g))

