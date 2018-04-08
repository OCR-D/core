# -*- coding: utf-8 -*-
import codecs

from setuptools import setup, find_packages

with codecs.open('README.rst', encoding='utf-8') as f:
    README = f.read()

with codecs.open('LICENSE', encoding='utf-8') as f:
    LICENSE = f.read()

setup(
    name='ocrd',
    version='0.0.1',
    description='OCR-D framework',
    long_description=README,
    author='Kay-Michael Würzner, Konstantin Baierer',
    author_email='wuerzner@bbaw.de',
    url='https://github.com/OCR-D/pyocrd',
    license=LICENSE,
    packages=find_packages(exclude=('tests', 'docs')),
    include_package_data=True,
    package_data={
        '': ['*.json'],
    },
    entry_points={
        'console_scripts': [
            'ocrd=ocrd.cli.run:cli',
        ]
    },
)
