.PHONY: style

style:
	pycodestyle *.py
	pycodestyle tools/*.py
lint:
	pylint *.py
	pylint tools/*.py
