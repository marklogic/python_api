all: test docs

.PHONY: invenv

test: invenv
	python3 setup.py test

docs: invenv
	sphinx-build -b html docs/source docs/_build

invenv:
	@python3 python_api/invirtual.py
