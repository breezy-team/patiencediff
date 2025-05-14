# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

patiencediff is a Python implementation of the "patience diff" algorithm first described by Bram Cohen. The package contains both a Python implementation and a faster C implementation of the algorithm.

Similar to Python's `difflib`, this module provides:
- A `unified_diff` function for generating unified diffs of text files
- A `SequenceMatcher` that can be used on arbitrary lists

The package was originally extracted from the Bazaar codebase and is now maintained by the Breezy team.

## Building and Installation

To build the package:

```bash
# Build the package (including C extension)
pip3 install -e .

# Build without C extension
CIBUILDWHEEL=1 pip install -e .
```

## Running Tests

Tests use Python's built-in unittest framework:

```bash
# Run all tests
python3 -m unittest discover patiencediff

# Run a specific test class
python3 -m unittest patiencediff.test_patiencediff.TestPatienceDiffLib

# Run a specific test method
python3 -m unittest patiencediff.test_patiencediff.TestPatienceDiffLib.test_unique_lcs
```

## Code Linting

The project uses ruff for linting:

```bash
# Install development dependencies (includes ruff)
pip install -e ".[dev]"

# Run linting
ruff .
```

## Using patiencediff

To use the patiencediff module from the command line:

```bash
python3 -m patiencediff file_a file_b

# Use standard difflib algorithm instead of patience
python3 -m patiencediff --difflib file_a file_b
```

From Python:

```python
import patiencediff

# Generate unified diff
diff = patiencediff.unified_diff(
    ['a\n', 'b\n', 'c\n'],
    ['a\n', 'x\n', 'c\n']
)
print(''.join(diff))

# Use SequenceMatcher for custom diff operations
matcher = patiencediff.PatienceSequenceMatcher(None, a_list, b_list)
```

## Code Architecture

The package consists of two implementations:

1. **Python implementation** (`_patiencediff_py.py`): Pure Python implementation of the algorithm, more readable but slower.

2. **C implementation** (`_patiencediff_c.c`): Faster implementation in C, requires a C compiler to build.

The entry point (`__init__.py`) tries to load the C implementation first, and falls back to the Python implementation if the C extension isn't available.

Key components:
- `unique_lcs`: Finds the longest common subsequence between two sequences
- `recurse_matches`: Recursively finds matches between two sequences
- `PatienceSequenceMatcher`: Main implementation of the diff algorithm, similar interface to `difflib.SequenceMatcher`
- `unified_diff`: Creates a unified diff from two sequences
- `unified_diff_files`: Reads two files and returns a unified diff
