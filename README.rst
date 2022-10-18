patiencediff
############

This package contains the implementation of the ``patiencediff`` algorithm, as
`first described <https://bramcohen.livejournal.com/73318.html>`_ by Bram Cohen.

Like Python's ``difflib``, this module provides both a convenience ``unified_diff``
function for the generation of unified diffs of text files
as well as a SequenceMatcher that can be used on arbitrary lists.

Patiencediff provides a good balance of performance, nice output for humans,
and implementation simplicity.

The code in this package was extracted from the `Bazaar <https://www.bazaar-vcs.org/>`_
code base.

The package comes with two implementations:

* A Python implementation (_patiencediff_py.py); this implementation only
  requires a Python interpreter and is the more readable version of the two

* A C implementation implementation (_patiencediff_c.c); this implementation
  is faster, but requires a C compiler and is less readable

Usage
=====

To invoke patiencediff from the command-line::

    python -m patiencediff file_a file_b

Or from Python:

     >>> import patiencediff
     >>> print ''.join(patiencediff.unified_diff(
     ...      ['a\n', 'b\n', 'b\n', 'c\n'],
     ...      ['a\n', 'c\n', 'b\n']))
     ---
     +++
     @@ -1,4 +1,3 @@
      a
     +c
      b
     -b
     -c
