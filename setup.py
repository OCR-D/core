# -*- coding: utf-8 -*-
import codecs

from setuptools import setup, find_packages

with codecs.open('README.rst', encoding='utf-8') as f:
    README = f.read()

setup(
    name='ocrd',
    version='0.8.6',
    description='OCR-D framework',
    long_description=README,
    author='Kay-Michael Würzner, Konstantin Baierer',
    author_email='wuerzner@bbaw.de',
    url='https://github.com/OCR-D/pyocrd',
    license='Apache License 2.0',
    packages=find_packages(exclude=('tests', 'docs')),
    include_package_data=True,
    install_requires=[
        'Flask',
        'Pillow',
        'click',
        'click >=7<8',
        'jsonschema',
        'lxml',
        'numpy',
        'opencv-python',
        'pyyaml',
        'requests',
        'Deprecated == 1.2.0',
    ],
    package_data={
        '': ['*.json', '*.yml', '*.yaml', '*.bash', '*.xml'],
    },
    entry_points={
        'console_scripts': [
            'ocrd=ocrd.cli:cli',
        ]
    },
)
