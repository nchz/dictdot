build:
	python setup.py bdist_wheel

lint:
	black --check --diff dictdot/
	flake8 dictdot/

test:
	pytest --cov dictdot tests.py

upload:
	twine upload -u ${PYPI_USER} -p ${PYPI_PASSWORD} dist/*

clean:
	rm -rf __pycache__/ build/ dictdot.egg-info/ dist/  .pytest_cache/ .coverage

.PHONY: build lint test upload clean
