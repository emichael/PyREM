Release Process
===============

1. Ensure tests are passing.

2. Ensure dependencies in `setup.py`, `requirements.txt`, and
   `requirements-dev.txt` are up to date.

3. Update `setup.py` and `docs/conf.py` with latest version number.

4. Commit latest changes to `develop` branch.

5. Build sdist and wheel (`python setup.py sdist bdist_wheel`).

6. Push to test PyPI server
   (`twine upload -r test -s dist/PyREM-0.1.1-py2.py3-none-any.whl dist/PyREM-0.1.1.tar.gz`).

7. Check test staging server version.

8. Push to PyPI
   (`twine upload -s dist/PyREM-0.1.1-py2.py3-none-any.whl dist/PyREM-0.1.1.tar.gz`).

9. Tag commit, push tag to GitHub.

10. Merge into `release` branch, push `release` and `develop` to GitHub.
