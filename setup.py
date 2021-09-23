import os

from setuptools import setup


HERE = os.path.abspath(os.path.dirname(__file__))

def read(*path):
    with open(os.path.join(HERE, *path), 'r') as f:
        return f.read()

################################################################################
NAME = 'PyREM'
DESCRIPTION = "Python Remote Experiment Runner"
VERSION = '0.2.0'
URL = 'https://github.com/emichael/PyREM'
AUTHOR = "Ellis Michael"
AUTHOR_EMAIL = 'ellis@ellismichael.com'
PACKAGES = ['pyrem']
KEYWORDS = ["remote management", "distributed", "experiment"]
LONG_DESCRIPTION = read('README.rst')
LICENSE = "MIT"
CLASSIFIERS = [
    'Development Status :: 2 - Pre-Alpha',
    'Intended Audience :: Science/Research',
    'Intended Audience :: System Administrators',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3',
    'Topic :: Scientific/Engineering',
    'Topic :: Software Development',
    'Topic :: System :: Distributed Computing'
]
INSTALL_REQUIRES = [
    'decorator>=4.0.2,<5'
]
PYTHON_VERSION = '>=3.4'
################################################################################

if __name__ == '__main__':
    setup(name=NAME,
          description=DESCRIPTION,
          version=VERSION,
          url=URL,
          author=AUTHOR,
          author_email=AUTHOR_EMAIL,
          packages=PACKAGES,
          keywords=KEYWORDS,
          long_description=LONG_DESCRIPTION,
          license=LICENSE,
          classifiers=CLASSIFIERS,
          install_requires=INSTALL_REQUIRES,
          python_requires=PYTHON_VERSION)
