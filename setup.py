#!/usr/bin/env python3

import os

from setuptools import setup
from setuptools_rust import Binding, RustExtension

# Rust extension
rust_extensions = [
    RustExtension(
        "patiencediff._patiencediff_rs",
        "Cargo.toml",
        binding=Binding.PyO3,
        optional=os.environ.get("CIBUILDWHEEL", "0") != "1",
    )
]

setup(
    rust_extensions=rust_extensions,
)
