.PHONY: clean clean-test clean-pyc clean-build docs help
.DEFAULT_GOAL := help

define BROWSER_PYSCRIPT
import os, webbrowser, sys

from urllib.request import pathname2url

webbrowser.open("file://" + pathname2url(os.path.abspath(sys.argv[1])))
endef
export BROWSER_PYSCRIPT

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

BROWSER := python -c "$$BROWSER_PYSCRIPT"

help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

clean: clean-build clean-pyc clean-test ## remove all build, test, coverage and Python artifacts

clean-build: ## remove build artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test: ## remove test and coverage artifacts
	rm -fr .tox/
	rm -f .coverage
	rm -fr htmlcov/
	rm -fr .pytest_cache

lint: ## check style with flake8
	@poetry run flake8 econci tests --statistics

test: ## run tests quickly with the default Python
	@poetry run pytest -vv --cov tests

coverage: ## check code coverage quickly with the default Python
	@poetry run pytest --cov=econci --cov-report=xml --cov-report=term-missing tests

docs: ## generate Sphinx HTML documentation, including API docs
	rm -f docs/econci.rst
	rm -f docs/modules.rst
	sphinx-apidoc -o docs/ econci
	$(MAKE) -C docs clean
	$(MAKE) -C docs html
	$(BROWSER) docs/_build/html/index.html

servedocs: docs ## compile the docs watching for changes
	watchmedo shell-command -p '*.rst' -c '$(MAKE) -C docs html' -R -D .

build: clean ## builds source and wheel package
	@poetry build
	ls -l dist

bump-patch:					## Bump version to next patch
	@poetry version patch

bump-minor:					## Bump version to next minor
	@poetry version minor

bump-major:					## Bump version to next major
	@poetry version major

prerelease:					## Create prerelase version
	@poetry version prerelease

publish: build check-env			## Publish new version to internal pypi (nexus)
	@poetry run twine upload dist/* --verbose

dependencies:
	@poetry install --no-dev

dev-dependencies: dependencies
	@poetry install
