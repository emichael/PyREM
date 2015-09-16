lint:
	pylint pyrem
	pep257 pyrem

clean:
	rm -rf build/ dist/
	find -name '*.pyc' -delete
