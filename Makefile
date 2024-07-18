.PHONY: all checkmake clean lint shellcheck style test unittest

all: checkmake shellcheck style lint test

checkmake:
	checkmake ./Makefile

clean:

lint:
	pylint --rcfile=./.pylintrc *.py || true
	pylint --rcfile=./.pylintrc tools/*.py || true
	pylint --rcfile=./.pylintrc tests/*.py || true

shellcheck:
	shellcheck tools/*.sh || true

style:
	pycodestyle *.py || true
	pycodestyle tools/*.py || true
	pycodestyle tests/*.py || true

unittest:
	python -m unittest tests/*.py

test: unittest
