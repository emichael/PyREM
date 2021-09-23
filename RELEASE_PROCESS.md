Release Process
===============

1. Ensure tests are passing.

2. Clean build directory (`make clean`).

3. Ensure dependencies in `setup.py`, `requirements.txt`, and
   `requirements-dev.txt` are up to date.

4. Update `setup.py` and `docs/conf.py` with latest version number.

5. Commit latest changes to `develop` branch.

6. Build sdist and wheel (`python setup.py sdist bdist_wheel`).

7. Push to test PyPI server
   (`twine upload -r testpypi -s dist/PyREM-*`).

8. Check test staging server version.

9. Push to PyPI
   (`twine upload -s dist/PyREM-*`).

10. Tag commit, push tag to GitHub.

11. Merge into `release` branch, push `release` and `develop` to GitHub.
