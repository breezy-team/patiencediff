#!/usr/bin/env python3
# encoding: utf-8

from setuptools import setup, Extension
from distutils import core

ext_modules = [
    Extension(
        'patiencediff._patiencediff_c',
        ['patiencediff/_patiencediff_c.c'])]


class Distribution(core.Distribution):

    def is_pure(self):
        if self.pure:
            return True

    def has_ext_modules(self):
        return not self.pure

    global_options = core.Distribution.global_options + [
        ('pure', None, "use pure Python code instead of C "
                       "extensions (slower on CPython)")]

    pure = False


setup(name="patiencediff",
      packages=['patiencediff'],
      test_suite='patiencediff.test_patiencediff',
      distclass=Distribution,
      ext_modules=ext_modules)
