.PHONY: all checkmake clean lint reqs shellcheck style test unittest

all: checkmake shellcheck style lint test

checkmake:
	checkmake ./Makefile

clean:

lint:
	pylint --rcfile=./.pylintrc ./tt/*.py || true
	pylint --rcfile=./.pylintrc ./tools/*.py || true
	pylint --rcfile=./.pylintrc ./tests/*.py || true

reqs:
	pipreqs --encoding utf-8

shellcheck:
	shellcheck tools/*.sh || true

style:
	pycodestyle ./tt/*.py || true
	pycodestyle ./tools/*.py || true
	pycodestyle ./tests/*.py || true

unittest:
	python -m unittest tests/*.py

test: unittest
