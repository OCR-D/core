# -*- coding: utf-8 -*-
import codecs

from setuptools import setup, find_packages

with codecs.open('README.rst', encoding='utf-8') as f:
    README = f.read()

setup(
    name='ocrd_models',
    version='0.8.8',
    description='OCR-D framework - File format wrappers',
    long_description=README,
    author='Konstantin Baierer',
    author_email='unixprog@gmail.com',
    url='https://github.com/OCR-D/core-models',
    license='Apache License 2.0',
    packages=find_packages(exclude=('tests', 'docs')),
    include_package_data=True,
    install_requires=[
        'ocrd_shared',
        'Pillow',
        'jsonschema',
        'lxml',
        'opencv-python',
        'pyyaml',
    ],
    package_data={
        '': ['*.json', '*.yml', '*.yaml', '*.bash', '*.xml'],
    }
)
