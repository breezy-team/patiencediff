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

import sys
import difflib

from . import PatienceSequenceMatcher, unified_diff_files


def main(argv=None):
    import optparse
    p = optparse.OptionParser(usage='%prog [options] file_a file_b'
                                    '\nFiles can be "-" to read from stdin')
    p.add_option('--patience', dest='matcher', action='store_const',
                 const='patience', default='patience',
                 help='Use the patience difference algorithm')
    p.add_option('--difflib', dest='matcher', action='store_const',
                 const='difflib',
                 default='patience', help='Use python\'s difflib algorithm')

    algorithms = {
        'patience': PatienceSequenceMatcher,
        'difflib': difflib.SequenceMatcher}

    (opts, args) = p.parse_args(argv)
    matcher = algorithms[opts.matcher]

    if len(args) != 2:
        print('You must supply 2 filenames to diff')
        return -1

    for line in unified_diff_files(args[0], args[1], sequencematcher=matcher):
        sys.stdout.write(line)


sys.exit(main(sys.argv[1:]))
