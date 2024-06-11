.PHONY: all checkmake clean lint shellcheck style test unittest

all: checkmake shellcheck style lint test

checkmake:
	checkmake ./Makefile

clean:

lint:
	pylint *.py || true
	pylint tools/*.py || true

shellcheck:
	shellcheck tools/*.sh || true

style:
	pycodestyle *.py || true
	pycodestyle tools/*.py || true

unittest:
	python -m unittest tests/*.py

test: unittest
