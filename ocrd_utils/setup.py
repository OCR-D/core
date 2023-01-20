# -*- coding: utf-8 -*-
from setuptools import setup

install_requires = open('requirements.txt').read().split('\n')

setup(
    name='ocrd_utils',
    version='2.45.1',
    description='OCR-D framework - shared code, helpers, constants',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Konstantin Baierer',
    author_email='unixprog@gmail.com',
    url='https://github.com/OCR-D/core',
    license='Apache License 2.0',
    packages=['ocrd_utils'],
    install_requires=install_requires,
    package_data={'': ['*.json', '*.yml', '*.xml']},
    keywords=['OCR', 'OCR-D']
)
