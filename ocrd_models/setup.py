# -*- coding: utf-8 -*-
from setuptools import setup, Command
from setuptools.command.build import build as orig_build

class build(orig_build):
    def finalize_options(self):
        vers = ' == ' + self.distribution.metadata.version
        self.distribution.install_requires = [
            req + vers if req.startswith('ocrd') and '==' not in req else req
            for req in self.distribution.install_requires
        ]
        orig_build.finalize_options(self)

setup(
    cmdclass={"build": build}
)
