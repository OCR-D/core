# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

from ocrd_utils import VERSION

install_requires = open('requirements.txt').read().split('\n')
install_requires.append('ocrd_utils == %s' % VERSION)
install_requires.append('ocrd_validators == %s' % VERSION)

# TODO: This needs to be revisited! Seems badly adapted from ocrd/setup.py
setup(
    name='ocrd_network',
    version=VERSION,
    description='OCR-D framework - web API',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Konstantin Baierer',
    author_email='unixprog@gmail.com',
    url='https://github.com/OCR-D/core',
    license='Apache License 2.0',
    packages=find_packages(exclude=('tests', 'docs')),
    include_package_data=True,
    install_requires=install_requires,
    package_data={
        '': ['*.yml', '*.xsd']
    },
    keywords=['OCR', 'OCR-D']
)
