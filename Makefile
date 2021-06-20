# Some simple testing tasks (sorry, UNIX only).

.PHONY: init setup
init setup:
	pip install -r requirements-dev.txt
	pre-commit install

.PHONY: fmt
fmt:
	python -m pre_commit run --all-files --show-diff-on-failure

.PHONY: lint
lint: fmt
	mypy

.PHONY: test
test:
	py.test -s ./tests/

.PHONY: clean
clean:
	rm -rf `find . -name __pycache__`
	rm -f `find . -type f -name '*.py[co]' `
	rm -f `find . -type f -name '*~' `
	rm -f `find . -type f -name '.*~' `
	rm -f `find . -type f -name '@*' `
	rm -f `find . -type f -name '#*#' `
	rm -f `find . -type f -name '*.orig' `
	rm -f `find . -type f -name '*.rej' `
	rm -f .coverage
	rm -rf coverage
	rm -rf build
	rm -rf cover

.PHONY: doc
doc:
	make -C docs html
	@echo "open file://`pwd`/docs/_build/html/index.html"
