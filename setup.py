# -*- coding: utf-8 -*-
import os
import os.path
from setuptools import find_packages
from setuptools import setup

name = 'snapper'
version = '0.0.5'


def find_requires():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    with open('{0}/requirements.txt'.format(dir_path), 'r') as reqs:
        requirements = reqs.readlines()
    return requirements


if __name__ == "__main__":
    setup(
        name=name,
        version=version,
        description='snapper tool using selenium',
        packages=find_packages(),
        install_requires=find_requires(),
        #add yaml part if  necessary
        #    
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