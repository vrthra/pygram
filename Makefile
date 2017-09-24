CONFIG=config.py

python2=python2
python3=python3
env=PYTHONPATH=.:./src:./libs:./tests PATH=$(PATH):~/.local/bin
lint=~/.local/bin/pylint

.PRECIOUS: %.js %.g


$(CONFIG): src/defaultconfig.py
	cat src/defaultconfig.py > config.py

nopyc:; find . -name \*.pyc | xargs rm

ff:;find * -not -type d -exec file '{}' ';'


working=t_accesslog


# strip_unused_self, strip_unused_rules

t_accesslog: $(CONFIG)
	$(env) $(python2) tests/t_accesslog.py
	@echo $(done)

t_apachelogparser: $(CONFIG)
	$(env) $(python2) tests/t_apachelogparser.py
	@echo $(done)



%.js: src/induce/Tracer.py
	$(env) $(python3) tests/$*.py data/$*.dat 2> $@.tmp
	mv $@.tmp $@

%.g: %.js
	$(env) $(python3) ./src/merge.py $? > $@.tmp
	cat $@.tmp
	mv $@.tmp $@

%.grammar:
	$(env) $(python3) tests/$*.py 3>&2 2>&1 1>&3 | $(env) $(python2) ./src/onlinemerge.py


lint:
	 $(python3) -m pylint src/induce/
