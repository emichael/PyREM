.PHONY: lint test clean

test:
	nosetests -w tests

lint:
	pylint pyrem
	pep257 pyrem

clean:
	rm -rf build/ dist/ .coverage
	find -name '*.pyc' -delete
	make -C docs clean
