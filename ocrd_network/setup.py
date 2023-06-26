# -*- coding: utf-8 -*-
from setuptools import setup
from ocrd_utils import VERSION

install_requires = open('requirements.txt').read().split('\n')
install_requires.append('ocrd_validators == %s' % VERSION)

setup(
    name='ocrd_network',
    version=VERSION,
    description='OCR-D framework - network',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Mehmed Mustafa, Jonas Schrewe, Triet Doan',
    author_email='unixprog@gmail.com',
    url='https://github.com/OCR-D/core',
    license='Apache License 2.0',
    python_requires=">=3.7",
    install_requires=install_requires,
    packages=[
        'ocrd_network',
        'ocrd_network.cli',
        'ocrd_network.models',
        'ocrd_network.rabbitmq_utils'
    ],
    keywords=['OCR', 'OCR-D']
)
