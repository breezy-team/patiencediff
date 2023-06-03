#!/usr/bin/env python3

import os

from setuptools import Extension, setup

ext_modules = [
    Extension(
        'patiencediff._patiencediff_c',
        ['patiencediff/_patiencediff_c.c'],
        optional=os.environ.get('CIBUILDWHEEL', '0') != '1')]


setup(ext_modules=ext_modules)
