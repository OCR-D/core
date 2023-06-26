# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
from ocrd_utils import VERSION

install_requires = open('requirements.txt').read().split('\n')
install_requires.append('ocrd_utils == %s' % VERSION)
install_requires.append('ocrd_models == %s' % VERSION)
install_requires.append('ocrd_modelfactory == %s' % VERSION)
install_requires.append('ocrd_validators == %s' % VERSION)
install_requires.append('ocrd_network == %s' % VERSION)

setup(
    name='ocrd',
    version=VERSION,
    description='OCR-D framework',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Konstantin Baierer',
    author_email='unixprog@gmail.com',
    url='https://github.com/OCR-D/core',
    license='Apache License 2.0',
    packages=find_packages(exclude=('tests', 'docs')),
    include_package_data=True,
    python_requires=">=3.7",
    install_requires=install_requires,
    entry_points={
        'console_scripts': [
            'ocrd=ocrd.cli:cli',
            'ocrd-dummy=ocrd.processor.builtin.dummy_processor:cli',
        ]
    },
)
