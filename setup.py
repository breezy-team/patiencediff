#!/usr/bin/env python3
# encoding: utf-8

from setuptools import setup, Extension
from distutils import core

with open('README.rst', 'r') as f:
    long_description = f.read()

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
      description="Python implementation of the patiencediff algorithm.",
      long_description=long_description,
      version="0.2.0",
      maintainer="Breezy Developers",
      maintainer_email="team@breezy-vcs.org",
      license="GNU GPLv2 or later",
      url="https://www.breezy-vcs.org/",
      packages=['patiencediff'],
      test_suite='patiencediff.test_patiencediff',
      distclass=Distribution,
      classifiers=[
          'Development Status :: 4 - Beta',
          'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',  # noqa
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: Implementation :: CPython',
          'Programming Language :: Python :: Implementation :: PyPy',
          'Operating System :: POSIX',
      ],
      ext_modules=ext_modules)
