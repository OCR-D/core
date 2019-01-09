# -*- coding: utf-8 -*-
from setuptools import setup

setup(
    name='ocrd_models',
    version='0.0.1',
    description='Engine independent OCR training',
    long_description=open('README.md'),
    long_description_content_type='text/markdown',
    author='Konstantin Baierer',
    author_email='unixprog@gmail.com',
    url='https://github.com/OCR-D/core',
    license='Apache License 2.0',
    install_requires=open('requirements.txt').read().split('\n'),
    packages=['ocrd_models'],
    package_data={'': ['*.json', '*.yml', '*.xml']},
    keywords=['OCR', 'OCR-D']
)
