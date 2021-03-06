# -*- coding: utf-8 -*-

import pathlib

import os
import os.path
from setuptools import find_packages
from setuptools import setup

name = 'snapper'

ROOT_DIR = pathlib.Path(__file__).parent


def find_description():
    dir_path = os.path.abspath(os.path.dirname(__file__))
    long_description = None
    with open(os.path.join(dir_path, 'README.md'), encoding='utf-8') as f:
        long_description = f.read()
    return long_description


def find_requires():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    with open('{0}/requirements.txt'.format(dir_path), 'r') as reqs:
        requirements = reqs.readlines()
    return requirements


def get_version():
    version_file = ROOT_DIR / "KVersion"
    with version_file.open() as ver:
        params = (l.strip().split("=") for l in ver if l.strip())
        semver = {
            k.strip(): v.strip()
            for k, v in params
        }
    return ".".join((semver['MAJOR'], semver['MINOR'], semver['FEATURE']))


if __name__ == "__main__":
    setup(
        name=name,
        version=get_version(),
        description='A security tool for grabbing screenshots of many web \
                     hosts.',
        packages=find_packages(),
        install_requires=find_requires(),
        long_description=find_description(),
        long_description_content_type='text/markdown',
        # add yaml part if  necessary
        data_files=[(
            'snapper',
            ['snapper/config.yaml']
        )],
        include_package_data=True,
        entry_points={
            'console_scripts': [
                'snap = snapper.cli:main',
            ],
        },
        classifiers=[
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
        ],
    )
