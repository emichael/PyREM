.PHONY: lint test clean

test:
	nosetests3 -w tests

lint:
	pylint pyrem
	pep257 pyrem

clean:
	rm -rf build/ dist/ .coverage PyREM.egg-info/
	find -name '*.pyc' -delete
	make -C docs clean
