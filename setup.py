from setuptools import setup

setup(name='PyREM',
      version='0.0.1',
      description="Python Remote Experiment Runner",
      install_requires=[
        'enum34>=1.0.4,<2',
        'ipython>=4,<5'
      ],
      packages=['pyrem'])
