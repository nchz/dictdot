all: lint test clean

build:
	python setup.py bdist_wheel

upload:
	twine upload -u ${PYPI_USER} -p ${PYPI_PASSWORD} dist/*

lint:
	black --check --diff dictdot/
	flake8 dictdot/

test:
	pytest --cov dictdot tests.py

clean:
	rm -rf __pycache__/ build/ dictdot.egg-info/ dist/  .pytest_cache/ .coverage

.PHONY: build lint test upload clean
