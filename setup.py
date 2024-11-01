#!/usr/bin/env python

import imp
import sys

from setuptools import setup, find_packages

if sys.version_info < (3, 6):
    sys.exit("Sorry, Python < 3.6 is not supported")


VERSION = imp.load_source("", "nwb_data_validator/version.py").__version__

setup(
    name="nwb-data-validator",
    author="BlueBrain Project, EPFL",
    version=VERSION,
    description="Quality control for the IGOR to NWB data conversion",
    url="https://github.com/BlueBrain/lnmc-nwb-conversion-validator",
    project_urls={
        "Tracker": "https://github.com/BlueBrain/lnmc-nwb-conversion-validator/issues",
        "Source": "https://github.com/BlueBrain/lnmc-nwb-conversion-validator",
    },
    license="Apache-2.0",
    install_requires=[
        "numpy",
        "bluepyefe",
        "pynwb",
        "pylatex",
        "tqdm",
        "pandas",
        "joblib",
        "ndx-icephys-meta @ git+ssh://git@github.com/oruebel/ndx-icephys-meta.git@2bd06bd152901ae5853253358d7efc66714f9a22",
    ],
    packages=find_packages(),
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
    ],
)
