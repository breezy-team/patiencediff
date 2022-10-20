#!/usr/bin/env python3
# encoding: utf-8

from setuptools import setup, Extension

ext_modules = [
    Extension(
        'patiencediff._patiencediff_c',
        ['patiencediff/_patiencediff_c.c'], optional=True)]


setup(ext_modules=ext_modules)
