# -*- coding: utf-8 -*-
from setuptools import setup
from ocrd_utils import VERSION

install_requires = open('requirements.txt').read().split('\n')
install_requires.append('ocrd_utils == %s' % VERSION)
install_requires.append('ocrd_validators == %s' % VERSION)

setup(
    name='ocrd_network',
    version=VERSION,
    description='OCR-D framework - network',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Konstantin Baierer',
    author_email='unixprog@gmail.com',
    url='https://github.com/OCR-D/core',
    license='Apache License 2.0',
    install_requires=install_requires,
    packages=['ocrd_network'],
    package_data={
        '': ['*.yml', '*.xsd']
    },
    keywords=['OCR', 'OCR-D']
)
