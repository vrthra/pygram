CONFIG=config.py

python2projects=\
tmicrojson \
tsimplejson \
tpysecjson \
turlparse \
turlparser \
tconfigobj \
tromannumerals \
tsqlparser \
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
teasydate \
tarrow \
tdateparser \
tapachelogparser \
taccesslog \
thttpresponse

python3projects=\
tnayajson \
tconfigparser

all: python2projects python3projects
	@echo done

python2projects: $(python2projects)

python3projects: $(python3projects)

done=""

tnayajson: $(CONFIG)
	python3 ./tests/t_nayajson.py ./data/json2.txt
	@echo $(done)

tmicrojson: $(CONFIG)
	python ./tests/t_microjson.py ./data/json2.txt
	@echo $(done)

tsimplejson: $(CONFIG)
	python ./tests/t_simplejson.py ./data/json2.txt
	@echo $(done)

tpysecjson: $(CONFIG)
	python ./tests/t_pysecjson.py
	@echo $(done)

turlparse: $(CONFIG)
	python ./tests/t_urlparse.py ./data/url_lines.txt
	@echo $(done)

turlparser: $(CONFIG)
	python ./tests/t_urlparser.py ./data/urltest_lines.txt
	@echo $(done)

tconfigparser: $(CONFIG)
	python3 ./tests/t_configparser.py ./data/configini.txt
	@echo $(done)

tconfigobj: $(CONFIG)
	python ./tests/t_configobj.py ./data/config.txt
	@echo $(done)

tromannumerals: $(CONFIG)
	python ./tests/t_romannumerals.py ./data/roman_lines.txt
	@echo $(done)

tsqlparser:  $(CONFIG)
	python ./tests/t_sqlparser.py ./data/sql_lines.txt
	@echo $(done)

tsimplesql: $(CONFIG)
	python ./tests/t_simplesql.py ./data/sql_lines2.txt
	@echo $(done)

tselectsql: $(CONFIG)
	python ./tests/t_selectsql.py ./data/sql_lines3.txt
	@echo $(done)

tsimpleselectsql: $(CONFIG)
	python ./tests/t_simpleselectsql.py ./data/simpleselectsql.txt
	@echo $(done)

tsimplearith: $(CONFIG)
	python ./tests/t_simplearith.py ./data/simplearith.txt
	@echo $(done)

tarith: $(CONFIG)
	python ./tests/t_arith.py ./data/arith.txt
	@echo $(done)

tpyexpressioneval: $(CONFIG)
	python ./tests/t_pyexpressioneval.py ./data/pyexpreval.txt
	@echo $(done)

tmathexpr: $(CONFIG)
	python ./tests/t_mathexpr.py ./data/mathexpr.txt
	@echo $(done)

tpgn: $(CONFIG)
	python ./tests/t_pgn.py ./data/pgn.txt
	@echo $(done)

tmicroc: $(CONFIG)
	python ./tests/t_microc.py ./data/microc.txt
	@echo $(done)

tcsubset: $(CONFIG)
	python ./tests/t_csubset.py ./data/csubset.txt
	@echo $(done)

tdeltatime: $(CONFIG)
	python ./tests/t_deltatime.py ./data/deltatime.txt
	@echo $(done)

tdatetime: $(CONFIG)
	python tests/t_datetime.py data/datetime.txt
	@echo $(done)

tdateutil: $(CONFIG)
	python tests/t_dateutil.py data/datetime.txt
	@echo $(done)

ttime: $(CONFIG)
	python tests/t_time.py data/datetime.txt
	@echo $(done)

teasydate: $(CONFIG)
	python tests/t_easydate.py data/datetime.txt
	@echo $(done)

tarrow: $(CONFIG)
	python tests/t_arrow.py data/time.txt
	@echo $(done)

tdateparser: $(CONFIG)
	python tests/t_dateparser.py data/dateparser.txt
	@echo $(done)

tapachelogparser: $(CONFIG)
	python tests/t_apachelogparser.py data/logs.txt
	@echo $(done)

taccesslog: $(CONFIG)
	python tests/t_accesslog.py data/accesslog.txt
	@echo $(done)

thttpresponse: $(CONFIG)
	python tests/t_httpresponse.py data/httpresponse.txt
	@echo $(done)


$(CONFIG): src/defaultconfig.py
	cat src/defaultconfig.py > config.py

nopyc:; find . -name \*.pyc | xargs rm

ff:;find * -not -type d -exec file '{}' ';'

