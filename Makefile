CONFIG=config.py

python2=python2
python3=python3
env=PYTHONPATH=.:./src:./libs:./tests

lint=~/.local/bin/pylint
pytest=~/.local/bin/pytest
jq=jq
test=~/.local/bin/py.test

.PRECIOUS: %.js %.g

commithooks:; echo make lint > .git/hooks/pre-commit; chmod +x .git/hooks/pre-commit

$(CONFIG): src/defaultconfig.py; cat src/defaultconfig.py > config.py

nopyc:
	find . -name \*.pyc -delete
	find . -name __pycache__ -delete

ff:;find * -not -type d -exec file '{}' ';'

%.js: src/induce/Tracer.py
	$(env) $(python3) examples/$*.py data/$*.dat 2> $@.tmp
	mv $@.tmp $@

%.g: %.js
	$(env) $(python3) ./src/merge.py $? > $@.tmp
	cat $@.tmp
	mv $@.tmp $@

%.jsx:
	$(env) $(python3) examples/$*.py data/$*.dat

%.grammar:
	$(env) $(python3) examples/$*.py data/$*.dat 3>&2 2>&1 1>&3 | $(env) $(python3) ./src/merge.py -

%.json: %.js
	cat $*.js | $(jq) '. | [ .func_name, .event, .id | tostring] | join(" ") '


lint: typecheck
	$(python3) -m pylint src/induce/


typecheck:
	$(python3) -m mypy --strict src/induce/

pytestflags=-vv
test:
	$(env) $(pytest) $(pytestflags) $(T)

utest:
	$(env) $(pytest) $(pytestflags) $(T) -k $(F)
