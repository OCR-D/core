# -*- coding: utf-8 -*-
import codecs

from setuptools import setup, find_packages

with codecs.open('README.rst', encoding='utf-8') as f:
    readme = f.read()

with codecs.open('LICENSE', encoding='utf-8') as f:
    license = f.read() # pylint: disable=redefined-builtin

setup(
    name='ocrd',
    version='0.0.1',
    description='OCR-D framework',
    long_description=readme,
    author='Kay-Michael Würzner, Konstantin Baierer',
    author_email='wuerzner@bbaw.de',
    url='https://github.com/OCR-D/pyocrd',
    license=license,
    packages=find_packages(exclude=('tests', 'docs')),
    install_requires=[
    ],
    entry_points={
        'console_scripts': [
            'ocrd=ocrd.cli.run:cli',
        ]
    },
)
