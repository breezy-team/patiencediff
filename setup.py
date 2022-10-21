#!/usr/bin/env python3
# encoding: utf-8

import os
from setuptools import setup, Extension


ext_modules = [
    Extension(
        'patiencediff._patiencediff_c',
        ['patiencediff/_patiencediff_c.c'],
        optional=os.environ.get('CIBUILDWHEEL', '0') != '1')]


setup(ext_modules=ext_modules)
