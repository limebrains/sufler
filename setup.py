#!/usr/bin/env python
from distutils.command.install_scripts import install_scripts
from distutils.core import setup

from setuptools import find_packages

import os
dir_path = os.path.dirname(os.path.realpath(__file__))
req_path = os.path.join(dir_path, 'requirements.txt')


class InstallScripts(install_scripts):
    def run(self):
        print("This line will never be printed")

    def get_outputs(self):
        return []


setup(
    name='sufler',
    version='0.0.1',
    description='Autocompletion Tool for Bash, Fish, Zsh, PowerShell',
    author='LimeBrains',
    author_email='mail@limebrains.com',
    url='https://github.com/limebrains/sufler',
    packages=find_packages(),
    include_package_data=True,
    install_requires=req_path,
    entry_points="""\
      [console_scripts]
      sufler = sufler.cli:main
    """,
    cmdclass={'install_scripts': InstallScripts},
    scripts=[],
)
