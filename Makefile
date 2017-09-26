CONFIG=config.py

python2=/usr/local/bin/python2
python3=/usr/local/bin/python3
env=PYTHONPATH=.:./src:./libs:./tests

lint=~/.local/bin/pylint
jq=jq

.PRECIOUS: %.js %.g

commithooks:; echo make lint > .git/hooks/pre-commit; chmod +x .git/hooks/pre-commit

$(CONFIG): src/defaultconfig.py; cat src/defaultconfig.py > config.py

nopyc:; find . -name \*.pyc | xargs rm

ff:;find * -not -type d -exec file '{}' ';'

%.js: src/induce/Tracer.py
	$(env) $(python3) tests/$*.py data/$*.dat 2> $@.tmp
	mv $@.tmp $@

%.g: %.js
	$(env) $(python3) ./src/merge.py $? > $@.tmp
	cat $@.tmp
	mv $@.tmp $@

%.jsx:
	$(env) $(python3) tests/$*.py data/$*.dat

%.grammar:
	$(env) $(python3) tests/$*.py 3>&2 2>&1 1>&3 | $(env) $(python3) ./src/onlinemerge.py

%.json: %.js
	cat $*.js | $(jq) '. | [ .func_name, .event, .id | tostring] | join(" ") '


lint: typecheck
	$(python3) -m pylint src/induce/


typecheck:
	$(python3) -m mypy src/induce/

