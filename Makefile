all: \
tnayajson \
tsqlparser \
tmicrojson \
turlparse \
tconfigobj \
tromannumerals \
tarith \
tsimplesql \
tselectsql \
tsimplearith \
tsimpleselectsql
	@echo done

done="_________________________________________________"


tnayajson: $(CONFIG)
	python3 ./tests/t_nayajson.py ./data/json2.txt
	@echo $(done)

tsqlparser:  $(CONFIG)
	python ./tests/t_sqlparser.py ./data/sql_lines.txt
	@echo $(done)

tmicrojson: $(CONFIG)
	python ./tests/t_microjson.py ./data/json2.txt
	@echo $(done)

turlparse: $(CONFIG)
	python ./tests/t_urlparse.py ./data/url_lines.txt
	@echo $(done)

turlparser: $(CONFIG)
	python ./tests/t_urlparser.py ./data/urltest_lines.txt
	@echo $(done)

tconfigobj: $(CONFIG)
	python ./tests/t_configobj.py ./data/config.txt
	@echo $(done)

tromannumerals: $(CONFIG)
	python ./tests/t_romannumerals.py ./data/roman_lines.txt
	@echo $(done)

tarith: $(CONFIG)
	python ./tests/t_arith.py ./data/arith.txt
	@echo $(done)

tsimplesql: $(CONFIG)
	python ./tests/t_simplesql.py ./data/sql_lines2.txt
	@echo $(done)

tselectsql: $(CONFIG)
	python ./tests/t_selectsql.py ./data/sql_lines3.txt
	@echo $(done)

tsimplearith: $(CONFIG)
	python ./tests/t_simplearith.py ./data/simplearith.txt
	@echo $(done)


tsimpleselectsql: $(CONFIG)
	python ./tests/t_simpleselectsql.py ./data/simpleselectsql.txt
	@echo $(done)


CONFIG=src/config.py

$(CONFIG): src/defaultconfig.py
	cat src/defaultconfig.py > config.py
