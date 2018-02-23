# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='ocrd',
    version='0.0.1',
    description='OCR-D framework',
    long_description=readme,
    author='Kay-Michael Würzner',
    author_email='wuerzner@bbaw.de',
    license=license,
    packages=find_packages(exclude=('tests', 'docs')),
    install_requires=[
    ],
    entry_points={
          'console_scripts': [
              'run-ocrd=ocrd.scripts.run:cli',
              'run-ocrd-server=ocrd.scripts.run_server:cli',
          ]
    },
)
