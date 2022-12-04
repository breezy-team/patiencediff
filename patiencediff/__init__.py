# Copyright (C) 2005, 2006, 2007 Canonical Ltd
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA

import os
import sys
import time
import difflib

from typing import Type


__all__ = ['PatienceSequenceMatcher', 'unified_diff', 'unified_diff_files']

__version__ = (0, 2, 10)


# This is a version of unified_diff which only adds a factory parameter
# so that you can override the default SequenceMatcher
# this has been submitted as a patch to python
def unified_diff(a, b, fromfile='', tofile='', fromfiledate='',
                 tofiledate='', n=3, lineterm='\n',
                 sequencematcher=None):
    r"""
    Compare two sequences of lines; generate the delta as a unified diff.

    Unified diffs are a compact way of showing line changes and a few
    lines of context.  The number of context lines is set by 'n' which
    defaults to three.

    By default, the diff control lines (those with ---, +++, or @@) are
    created with a trailing newline.  This is helpful so that inputs
    created from file.readlines() result in diffs that are suitable for
    file.writelines() since both the inputs and outputs have trailing
    newlines.

    For inputs that do not have trailing newlines, set the lineterm
    argument to "" so that the output will be uniformly newline free.

    The unidiff format normally has a header for filenames and modification
    times.  Any or all of these may be specified using strings for
    'fromfile', 'tofile', 'fromfiledate', and 'tofiledate'.  The modification
    times are normally expressed in the format returned by time.ctime().

    Example:

    >>> for line in unified_diff('one two three four'.split(),
    ...             'zero one tree four'.split(), 'Original', 'Current',
    ...             'Sat Jan 26 23:30:50 1991', 'Fri Jun 06 10:20:52 2003',
    ...             lineterm=''):
    ...     print line
    --- Original Sat Jan 26 23:30:50 1991
    +++ Current Fri Jun 06 10:20:52 2003
    @@ -1,4 +1,4 @@
    +zero
     one
    -two
    -three
    +tree
     four
    """
    if sequencematcher is None:
        sequencematcher = difflib.SequenceMatcher

    if fromfiledate:
        fromfiledate = '\t' + str(fromfiledate)
    if tofiledate:
        tofiledate = '\t' + str(tofiledate)

    started = False
    for group in sequencematcher(None, a, b).get_grouped_opcodes(n):
        if not started:
            yield '--- %s%s%s' % (fromfile, fromfiledate, lineterm)
            yield '+++ %s%s%s' % (tofile, tofiledate, lineterm)
            started = True
        i1, i2, j1, j2 = group[0][1], group[-1][2], group[0][3], group[-1][4]
        yield "@@ -%d,%d +%d,%d @@%s" % (i1+1, i2-i1, j1+1, j2-j1, lineterm)
        for tag, i1, i2, j1, j2 in group:
            if tag == 'equal':
                for line in a[i1:i2]:
                    yield ' ' + line
                continue
            if tag == 'replace' or tag == 'delete':
                for line in a[i1:i2]:
                    yield '-' + line
            if tag == 'replace' or tag == 'insert':
                for line in b[j1:j2]:
                    yield '+' + line


def unified_diff_files(a, b, sequencematcher=None):
    """Generate the diff for two files.
    """
    # Should this actually be an error?
    if a == b:
        return []
    if a == '-':
        lines_a = sys.stdin.readlines()
        time_a = time.time()
    else:
        with open(a, 'r') as f:
            lines_a = f.readlines()
        time_a = os.stat(a).st_mtime  # noqa: F841

    if b == '-':
        lines_b = sys.stdin.readlines()
        time_b = time.time()
    else:
        with open(b, 'r') as f:
            lines_b = f.readlines()
        time_b = os.stat(b).st_mtime  # noqa: F841

    # TODO: Include fromfiledate and tofiledate
    return unified_diff(lines_a, lines_b,
                        fromfile=a, tofile=b,
                        sequencematcher=sequencematcher)


PatienceSequenceMatcher: Type[difflib.SequenceMatcher]


try:
    from ._patiencediff_c import (
        unique_lcs_c as unique_lcs,
        recurse_matches_c as recurse_matches,
        PatienceSequenceMatcher_c as PatienceSequenceMatcher
        )
except ImportError:
    from ._patiencediff_py import (  # noqa: F401
        unique_lcs_py as unique_lcs,
        recurse_matches_py as recurse_matches,
        PatienceSequenceMatcher_py as PatienceSequenceMatcher
        )
