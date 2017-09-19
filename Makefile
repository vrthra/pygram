CONFIG=config.py

python2=python2
python3=python3
env=PYTHONPATH=.:./src:./libs:./tests

python2projects=\
tmicrojson \
turlparse \
turlparser \
tconfigobj \
tromannumerals \
tsimplesql \
tselectsql \
tsimpleselectsql \
tsimplearith \
tarith \
tpyexpressioneval \
tmathexpr \
tpgn \
tmicroc \
tcsubset \
tdeltatime \
tdatetime \
tdateutil \
ttime \
taccesslog \
thttpresponse

withpip2=tsimplejson \
tpysecjson \
tsqlparser \
teasydate \
tarrow \
tdateparser \
tapachelogparser \

python3projects=\
tnayajson \
tconfigparser

all: python2projects python3projects
	@echo done

python2nopip: $(python2projects)

python2projects: $(python2projects) $(withpip2)

python3projects: $(python3projects)

done=""

tnayajson: $(CONFIG)
	$(env) $(python3) ./tests/t_nayajson.py ./data/json2.txt
	@echo $(done)

tmicrojson: $(CONFIG)
	$(env) $(python2) ./tests/t_microjson.py ./data/json2.txt
	@echo $(done)

tsimplejson: $(CONFIG)
	$(env) $(python2) ./tests/t_simplejson.py ./data/json2.txt
	@echo $(done)

tpysecjson: $(CONFIG)
	$(env) $(python2) ./tests/t_pysecjson.py
	@echo $(done)

turlparse: $(CONFIG)
	$(env) $(python2) ./tests/t_urlparse.py ./data/url_lines.txt
	@echo $(done)

turlparser: $(CONFIG)
	$(env) $(python2) ./tests/t_urlparser.py ./data/urltest_lines.txt
	@echo $(done)

tconfigparser: $(CONFIG)
	$(env) $(python3) ./tests/t_configparser.py ./data/configini.txt
	@echo $(done)

tconfigobj: $(CONFIG)
	$(env) $(python2) ./tests/t_configobj.py ./data/config.txt
	@echo $(done)

tromannumerals: $(CONFIG)
	$(env) $(python2) ./tests/t_romannumerals.py ./data/roman_lines.txt
	@echo $(done)

tsqlparser:  $(CONFIG)
	$(env) $(python2) ./tests/t_sqlparser.py ./data/sql_lines.txt
	@echo $(done)

tsimplesql: $(CONFIG)
	$(env) $(python2) ./tests/t_simplesql.py ./data/sql_lines2.txt
	@echo $(done)

tselectsql: $(CONFIG)
	$(env) $(python2) ./tests/t_selectsql.py ./data/sql_lines3.txt
	@echo $(done)

tsimpleselectsql: $(CONFIG)
	$(env) $(python2) ./tests/t_simpleselectsql.py ./data/simpleselectsql.txt
	@echo $(done)

tsimplearith: $(CONFIG)
	$(env) $(python2) ./tests/t_simplearith.py ./data/simplearith.txt
	@echo $(done)

tarith: $(CONFIG)
	$(env) $(python2) ./tests/t_arith.py ./data/arith.txt
	@echo $(done)

tpyexpressioneval: $(CONFIG)
	$(env) $(python2) ./tests/t_pyexpressioneval.py ./data/pyexpreval.txt
	@echo $(done)

tmathexpr: $(CONFIG)
	$(env) $(python2) ./tests/t_mathexpr.py ./data/mathexpr.txt
	@echo $(done)

tpgn: $(CONFIG)
	$(env) $(python2) ./tests/t_pgn.py ./data/pgn.txt
	@echo $(done)

tmicroc: $(CONFIG)
	$(env) $(python2) ./tests/t_microc.py ./data/microc.txt
	@echo $(done)

tcsubset: $(CONFIG)
	$(env) $(python2) ./tests/t_csubset.py ./data/csubset.txt
	@echo $(done)

tdeltatime: $(CONFIG)
	$(env) $(python2) ./tests/t_deltatime.py ./data/deltatime.txt
	@echo $(done)

tdatetime: $(CONFIG)
	$(env) $(python2) tests/t_datetime.py data/datetime.txt
	@echo $(done)

tdateutil: $(CONFIG)
	$(env) $(python2) tests/t_dateutil.py data/datetime.txt
	@echo $(done)

ttime: $(CONFIG)
	$(env) $(python2) tests/t_time.py data/datetime.txt
	@echo $(done)

teasydate: $(CONFIG)
	$(env) $(python2) tests/t_easydate.py data/datetime.txt
	@echo $(done)

tarrow: $(CONFIG)
	$(env) $(python2) tests/t_arrow.py data/time.txt
	@echo $(done)

tdateparser: $(CONFIG)
	$(env) $(python2) tests/t_dateparser.py data/dateparser.txt
	@echo $(done)

tapachelogparser: $(CONFIG)
	$(env) $(python2) tests/t_apachelogparser.py data/logs.txt
	@echo $(done)

taccesslog: $(CONFIG)
	$(env) $(python2) tests/t_accesslog.py data/accesslog.txt
	@echo $(done)

thttpresponse: $(CONFIG)
	$(env) $(python2) tests/t_httpresponse.py data/httpresponse.txt
	@echo $(done)


$(CONFIG): src/defaultconfig.py
	cat src/defaultconfig.py > config.py

nopyc:; find . -name \*.pyc | xargs rm

ff:;find * -not -type d -exec file '{}' ';'


t_accesslog: $(CONFIG)
	$(env) $(python2) tests/t_accesslog.py
	@echo $(done)

t_apachelogparser: $(CONFIG)
	$(env) $(python2) tests/t_apachelogparser.py
	@echo $(done)



accesslog.js: src/induce/Tracer.py
	$(env) $(python2) tests/t_accesslog.py > $@.tmp
	mv $@.tmp $@

accesslog.grammar: accesslog.js
	$(env) $(python2) ./src/merge.py accesslog.js

