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
import patiencediff
import shutil
import sys
import tempfile
import unittest

from . import _patiencediff_py


if sys.version_info[0] == 3:
    unichr = chr


class TestPatienceDiffLib(unittest.TestCase):

    def setUp(self):
        super(TestPatienceDiffLib, self).setUp()
        self._unique_lcs = _patiencediff_py.unique_lcs_py
        self._recurse_matches = _patiencediff_py.recurse_matches_py
        self._PatienceSequenceMatcher = \
            _patiencediff_py.PatienceSequenceMatcher_py

    def test_diff_unicode_string(self):
        a = ''.join([unichr(i) for i in range(4000, 4500, 3)])
        b = ''.join([unichr(i) for i in range(4300, 4800, 2)])
        sm = self._PatienceSequenceMatcher(None, a, b)
        mb = sm.get_matching_blocks()
        self.assertEqual(35, len(mb))

    def test_unique_lcs(self):
        unique_lcs = self._unique_lcs
        self.assertEqual(unique_lcs('', ''), [])
        self.assertEqual(unique_lcs('', 'a'), [])
        self.assertEqual(unique_lcs('a', ''), [])
        self.assertEqual(unique_lcs('a', 'a'), [(0, 0)])
        self.assertEqual(unique_lcs('a', 'b'), [])
        self.assertEqual(unique_lcs('ab', 'ab'), [(0, 0), (1, 1)])
        self.assertEqual(
            unique_lcs('abcde', 'cdeab'), [(2, 0), (3, 1), (4, 2)])
        self.assertEqual(
            unique_lcs('cdeab', 'abcde'), [(0, 2), (1, 3), (2, 4)])
        self.assertEqual(
            unique_lcs('abXde', 'abYde'), [(0, 0), (1, 1), (3, 3), (4, 4)])
        self.assertEqual(unique_lcs('acbac', 'abc'), [(2, 1)])

    def test_recurse_matches(self):
        def test_one(a, b, matches):
            test_matches = []
            self._recurse_matches(
                a, b, 0, 0, len(a), len(b), test_matches, 10)
            self.assertEqual(test_matches, matches)

        test_one(['a', '', 'b', '', 'c'], ['a', 'a', 'b', 'c', 'c'],
                 [(0, 0), (2, 2), (4, 4)])
        test_one(['a', 'c', 'b', 'a', 'c'], ['a', 'b', 'c'],
                 [(0, 0), (2, 1), (4, 2)])
        # Even though 'bc' is not unique globally, and is surrounded by
        # non-matching lines, we should still match, because they are locally
        # unique
        test_one('abcdbce', 'afbcgdbce', [(0, 0), (1, 2), (2, 3), (3, 5),
                                          (4, 6), (5, 7), (6, 8)])

        # recurse_matches doesn't match non-unique
        # lines surrounded by bogus text.
        # The update has been done in patiencediff.SequenceMatcher instead

        # This is what it could be
        # test_one('aBccDe', 'abccde', [(0,0), (2,2), (3,3), (5,5)])

        # This is what it currently gives:
        test_one('aBccDe', 'abccde', [(0, 0), (5, 5)])

    def assertDiffBlocks(self, a, b, expected_blocks):
        """Check that the sequence matcher returns the correct blocks.

        :param a: A sequence to match
        :param b: Another sequence to match
        :param expected_blocks: The expected output, not including the final
            matching block (len(a), len(b), 0)
        """
        matcher = self._PatienceSequenceMatcher(None, a, b)
        blocks = matcher.get_matching_blocks()
        last = blocks.pop()
        self.assertEqual((len(a), len(b), 0), last)
        self.assertEqual(expected_blocks, blocks)

    def test_matching_blocks(self):
        # Some basic matching tests
        self.assertDiffBlocks('', '', [])
        self.assertDiffBlocks([], [], [])
        self.assertDiffBlocks('abc', '', [])
        self.assertDiffBlocks('', 'abc', [])
        self.assertDiffBlocks('abcd', 'abcd', [(0, 0, 4)])
        self.assertDiffBlocks('abcd', 'abce', [(0, 0, 3)])
        self.assertDiffBlocks('eabc', 'abce', [(1, 0, 3)])
        self.assertDiffBlocks('eabce', 'abce', [(1, 0, 4)])
        self.assertDiffBlocks('abcde', 'abXde', [(0, 0, 2), (3, 3, 2)])
        self.assertDiffBlocks('abcde', 'abXYZde', [(0, 0, 2), (3, 5, 2)])
        self.assertDiffBlocks('abde', 'abXYZde', [(0, 0, 2), (2, 5, 2)])
        # This may check too much, but it checks to see that
        # a copied block stays attached to the previous section,
        # not the later one.
        # difflib would tend to grab the trailing longest match
        # which would make the diff not look right
        self.assertDiffBlocks('abcdefghijklmnop', 'abcdefxydefghijklmnop',
                              [(0, 0, 6), (6, 11, 10)])

        # make sure it supports passing in lists
        self.assertDiffBlocks(
               ['hello there\n',
                'world\n',
                'how are you today?\n'],
               ['hello there\n',
                'how are you today?\n'],
               [(0, 0, 1), (2, 1, 1)])

        # non unique lines surrounded by non-matching lines
        # won't be found
        self.assertDiffBlocks('aBccDe', 'abccde', [(0, 0, 1), (5, 5, 1)])

        # But they only need to be locally unique
        self.assertDiffBlocks(
            'aBcDec', 'abcdec', [(0, 0, 1), (2, 2, 1), (4, 4, 2)])

        # non unique blocks won't be matched
        self.assertDiffBlocks('aBcdEcdFg', 'abcdecdfg', [(0, 0, 1), (8, 8, 1)])

        # but locally unique ones will
        self.assertDiffBlocks(
            'aBcdEeXcdFg', 'abcdecdfg',
            [(0, 0, 1), (2, 2, 2), (5, 4, 1), (7, 5, 2), (10, 8, 1)])

        self.assertDiffBlocks('abbabbXd', 'cabbabxd', [(7, 7, 1)])
        self.assertDiffBlocks('abbabbbb', 'cabbabbc', [])
        self.assertDiffBlocks('bbbbbbbb', 'cbbbbbbc', [])

    def test_matching_blocks_tuples(self):
        # Some basic matching tests
        self.assertDiffBlocks([], [], [])
        self.assertDiffBlocks([('a',), ('b',), ('c,')], [], [])
        self.assertDiffBlocks([], [('a',), ('b',), ('c,')], [])
        self.assertDiffBlocks([('a',), ('b',), ('c,')],
                              [('a',), ('b',), ('c,')],
                              [(0, 0, 3)])
        self.assertDiffBlocks([('a',), ('b',), ('c,')],
                              [('a',), ('b',), ('d,')],
                              [(0, 0, 2)])
        self.assertDiffBlocks([('d',), ('b',), ('c,')],
                              [('a',), ('b',), ('c,')],
                              [(1, 1, 2)])
        self.assertDiffBlocks([('d',), ('a',), ('b',), ('c,')],
                              [('a',), ('b',), ('c,')],
                              [(1, 0, 3)])
        self.assertDiffBlocks([('a', 'b'), ('c', 'd'), ('e', 'f')],
                              [('a', 'b'), ('c', 'X'), ('e', 'f')],
                              [(0, 0, 1), (2, 2, 1)])
        self.assertDiffBlocks([('a', 'b'), ('c', 'd'), ('e', 'f')],
                              [('a', 'b'), ('c', 'dX'), ('e', 'f')],
                              [(0, 0, 1), (2, 2, 1)])

    def test_opcodes(self):
        def chk_ops(a, b, expected_codes):
            s = self._PatienceSequenceMatcher(None, a, b)
            self.assertEqual(expected_codes, s.get_opcodes())

        chk_ops('', '', [])
        chk_ops([], [], [])
        chk_ops('abc', '', [('delete', 0, 3, 0, 0)])
        chk_ops('', 'abc', [('insert', 0, 0, 0, 3)])
        chk_ops('abcd', 'abcd', [('equal',    0, 4, 0, 4)])
        chk_ops('abcd', 'abce', [('equal',   0, 3, 0, 3),
                                 ('replace', 3, 4, 3, 4)
                                 ])
        chk_ops('eabc', 'abce', [('delete', 0, 1, 0, 0),
                                 ('equal',  1, 4, 0, 3),
                                 ('insert', 4, 4, 3, 4)
                                 ])
        chk_ops('eabce', 'abce', [('delete', 0, 1, 0, 0),
                                  ('equal',  1, 5, 0, 4)
                                  ])
        chk_ops('abcde', 'abXde', [('equal',   0, 2, 0, 2),
                                   ('replace', 2, 3, 2, 3),
                                   ('equal',   3, 5, 3, 5)
                                   ])
        chk_ops('abcde', 'abXYZde', [('equal',   0, 2, 0, 2),
                                     ('replace', 2, 3, 2, 5),
                                     ('equal',   3, 5, 5, 7)
                                     ])
        chk_ops('abde', 'abXYZde', [('equal',  0, 2, 0, 2),
                                    ('insert', 2, 2, 2, 5),
                                    ('equal',  2, 4, 5, 7)
                                    ])
        chk_ops('abcdefghijklmnop', 'abcdefxydefghijklmnop',
                [('equal',  0, 6,  0, 6),
                 ('insert', 6, 6,  6, 11),
                 ('equal',  6, 16, 11, 21)
                 ])
        chk_ops(
                ['hello there\n', 'world\n', 'how are you today?\n'],
                ['hello there\n', 'how are you today?\n'],
                [('equal',  0, 1, 0, 1),
                 ('delete', 1, 2, 1, 1),
                 ('equal',  2, 3, 1, 2),
                 ])
        chk_ops('aBccDe', 'abccde',
                [('equal',   0, 1, 0, 1),
                 ('replace', 1, 5, 1, 5),
                 ('equal',   5, 6, 5, 6),
                 ])
        chk_ops('aBcDec', 'abcdec',
                [('equal',   0, 1, 0, 1),
                 ('replace', 1, 2, 1, 2),
                 ('equal',   2, 3, 2, 3),
                 ('replace', 3, 4, 3, 4),
                 ('equal',   4, 6, 4, 6),
                 ])
        chk_ops('aBcdEcdFg', 'abcdecdfg',
                [('equal',   0, 1, 0, 1),
                 ('replace', 1, 8, 1, 8),
                 ('equal',   8, 9, 8, 9)
                 ])
        chk_ops('aBcdEeXcdFg', 'abcdecdfg',
                [('equal',   0, 1, 0, 1),
                 ('replace', 1, 2, 1, 2),
                 ('equal',   2, 4, 2, 4),
                 ('delete', 4, 5, 4, 4),
                 ('equal',   5, 6, 4, 5),
                 ('delete', 6, 7, 5, 5),
                 ('equal',   7, 9, 5, 7),
                 ('replace', 9, 10, 7, 8),
                 ('equal',   10, 11, 8, 9)
                 ])

    def test_grouped_opcodes(self):
        def chk_ops(a, b, expected_codes, n=3):
            s = self._PatienceSequenceMatcher(None, a, b)
            self.assertEqual(expected_codes, list(s.get_grouped_opcodes(n)))

        chk_ops('', '', [])
        chk_ops([], [], [])
        chk_ops('abc', '', [[('delete', 0, 3, 0, 0)]])
        chk_ops('', 'abc', [[('insert', 0, 0, 0, 3)]])
        chk_ops('abcd', 'abcd', [])
        chk_ops('abcd', 'abce', [[('equal',   0, 3, 0, 3),
                                  ('replace', 3, 4, 3, 4)
                                  ]])
        chk_ops('eabc', 'abce', [[('delete', 0, 1, 0, 0),
                                 ('equal',  1, 4, 0, 3),
                                 ('insert', 4, 4, 3, 4)]])
        chk_ops('abcdefghijklmnop', 'abcdefxydefghijklmnop',
                [[('equal',  3, 6, 3, 6),
                  ('insert', 6, 6, 6, 11),
                  ('equal',  6, 9, 11, 14)
                  ]])
        chk_ops('abcdefghijklmnop', 'abcdefxydefghijklmnop',
                [[('equal',  2, 6, 2, 6),
                  ('insert', 6, 6, 6, 11),
                  ('equal',  6, 10, 11, 15)
                  ]], 4)
        chk_ops('Xabcdef', 'abcdef',
                [[('delete', 0, 1, 0, 0),
                  ('equal',  1, 4, 0, 3)
                  ]])
        chk_ops('abcdef', 'abcdefX',
                [[('equal',  3, 6, 3, 6),
                  ('insert', 6, 6, 6, 7)
                  ]])

    def test_multiple_ranges(self):
        # There was an earlier bug where we used a bad set of ranges,
        # this triggers that specific bug, to make sure it doesn't regress
        self.assertDiffBlocks('abcdefghijklmnop',
                              'abcXghiYZQRSTUVWXYZijklmnop',
                              [(0, 0, 3), (6, 4, 3), (9, 20, 7)])

        self.assertDiffBlocks('ABCd efghIjk  L',
                              'AxyzBCn mo pqrstuvwI1 2  L',
                              [(0, 0, 1), (1, 4, 2), (9, 19, 1), (12, 23, 3)])

        # These are rot13 code snippets.
        self.assertDiffBlocks('''\
    trg nqqrq jura lbh nqq n svyr va gur qverpgbel.
    """
    gnxrf_netf = ['svyr*']
    gnxrf_bcgvbaf = ['ab-erphefr']

    qrs eha(frys, svyr_yvfg, ab_erphefr=Snyfr):
        sebz omeyvo.nqq vzcbeg fzneg_nqq, nqq_ercbegre_cevag, nqq_ercbegre_ahyy
        vs vf_dhvrg():
            ercbegre = nqq_ercbegre_ahyy
        ryfr:
            ercbegre = nqq_ercbegre_cevag
        fzneg_nqq(svyr_yvfg, abg ab_erphefr, ercbegre)


pynff pzq_zxqve(Pbzznaq):
'''.splitlines(True), '''\
    trg nqqrq jura lbh nqq n svyr va gur qverpgbel.

    --qel-eha jvyy fubj juvpu svyrf jbhyq or nqqrq, ohg abg npghnyyl
    nqq gurz.
    """
    gnxrf_netf = ['svyr*']
    gnxrf_bcgvbaf = ['ab-erphefr', 'qel-eha']

    qrs eha(frys, svyr_yvfg, ab_erphefr=Snyfr, qel_eha=Snyfr):
        vzcbeg omeyvo.nqq

        vs qel_eha:
            vs vf_dhvrg():
                # Guvf vf cbvagyrff, ohg V'q engure abg envfr na reebe
                npgvba = omeyvo.nqq.nqq_npgvba_ahyy
            ryfr:
  npgvba = omeyvo.nqq.nqq_npgvba_cevag
        ryvs vf_dhvrg():
            npgvba = omeyvo.nqq.nqq_npgvba_nqq
        ryfr:
       npgvba = omeyvo.nqq.nqq_npgvba_nqq_naq_cevag

        omeyvo.nqq.fzneg_nqq(svyr_yvfg, abg ab_erphefr, npgvba)


pynff pzq_zxqve(Pbzznaq):
'''.splitlines(True), [(0, 0, 1), (1, 4, 2), (9, 19, 1), (12, 23, 3)])

    def test_patience_unified_diff(self):
        txt_a = ['hello there\n',
                 'world\n',
                 'how are you today?\n']
        txt_b = ['hello there\n',
                 'how are you today?\n']
        unified_diff = patiencediff.unified_diff
        psm = self._PatienceSequenceMatcher
        self.assertEqual(['--- \n',
                          '+++ \n',
                          '@@ -1,3 +1,2 @@\n',
                          ' hello there\n',
                          '-world\n',
                          ' how are you today?\n'
                          ], list(unified_diff(
                             txt_a, txt_b, sequencematcher=psm)))
        txt_a = [x+'\n' for x in 'abcdefghijklmnop']
        txt_b = [x+'\n' for x in 'abcdefxydefghijklmnop']
        # This is the result with LongestCommonSubstring matching
        self.assertEqual(['--- \n',
                          '+++ \n',
                          '@@ -1,6 +1,11 @@\n',
                          ' a\n',
                          ' b\n',
                          ' c\n',
                          '+d\n',
                          '+e\n',
                          '+f\n',
                          '+x\n',
                          '+y\n',
                          ' d\n',
                          ' e\n',
                          ' f\n'], list(unified_diff(txt_a, txt_b)))
        # And the patience diff
        self.assertEqual(['--- \n',
                          '+++ \n',
                          '@@ -4,6 +4,11 @@\n',
                          ' d\n',
                          ' e\n',
                          ' f\n',
                          '+x\n',
                          '+y\n',
                          '+d\n',
                          '+e\n',
                          '+f\n',
                          ' g\n',
                          ' h\n',
                          ' i\n',
                          ], list(unified_diff(
                              txt_a, txt_b, sequencematcher=psm)))

    def test_patience_unified_diff_with_dates(self):
        txt_a = ['hello there\n',
                 'world\n',
                 'how are you today?\n']
        txt_b = ['hello there\n',
                 'how are you today?\n']
        unified_diff = patiencediff.unified_diff
        psm = self._PatienceSequenceMatcher
        self.assertEqual(['--- a\t2008-08-08\n',
                          '+++ b\t2008-09-09\n',
                          '@@ -1,3 +1,2 @@\n',
                          ' hello there\n',
                          '-world\n',
                          ' how are you today?\n'
                          ], list(unified_diff(
                              txt_a, txt_b, fromfile='a', tofile='b',
                              fromfiledate='2008-08-08',
                              tofiledate='2008-09-09',
                              sequencematcher=psm)))


class TestPatienceDiffLib_c(TestPatienceDiffLib):

    def setUp(self):
        super(TestPatienceDiffLib_c, self).setUp()
        try:
            from . import _patiencediff_c
        except ImportError:
            self.skipTest('C extension not built')
        self._unique_lcs = _patiencediff_c.unique_lcs_c
        self._recurse_matches = _patiencediff_c.recurse_matches_c
        self._PatienceSequenceMatcher = \
            _patiencediff_c.PatienceSequenceMatcher_c

    def test_unhashable(self):
        """We should get a proper exception here."""
        # We need to be able to hash items in the sequence, lists are
        # unhashable, and thus cannot be diffed
        self.assertRaises(
            TypeError, self._PatienceSequenceMatcher, None, [[]], [])
        self.assertRaises(
            TypeError, self._PatienceSequenceMatcher, None,
            ['valid', []], [])
        self.assertRaises(
            TypeError, self._PatienceSequenceMatcher, None, ['valid'], [[]])
        self.assertRaises(
            TypeError, self._PatienceSequenceMatcher, None, ['valid'],
            ['valid', []])


class TestPatienceDiffLibFiles(unittest.TestCase):

    def setUp(self):
        super(TestPatienceDiffLibFiles, self).setUp()
        self._PatienceSequenceMatcher = \
            _patiencediff_py.PatienceSequenceMatcher_py
        self.test_dir = tempfile.mkdtemp()
        self.addCleanup(lambda: shutil.rmtree(self.test_dir))

    def test_patience_unified_diff_files(self):
        txt_a = [b'hello there\n',
                 b'world\n',
                 b'how are you today?\n']
        txt_b = [b'hello there\n',
                 b'how are you today?\n']
        with open(os.path.join(self.test_dir, 'a1'), 'wb') as f:
            f.writelines(txt_a)
        with open(os.path.join(self.test_dir, 'b1'), 'wb') as f:
            f.writelines(txt_b)

        unified_diff_files = patiencediff.unified_diff_files
        psm = self._PatienceSequenceMatcher

        old_pwd = os.getcwd()
        os.chdir(self.test_dir)
        try:
            self.assertEqual(['--- a1\n',
                              '+++ b1\n',
                              '@@ -1,3 +1,2 @@\n',
                              ' hello there\n',
                              '-world\n',
                              ' how are you today?\n',
                              ], list(unified_diff_files(
                                  'a1', 'b1', sequencematcher=psm)))
        finally:
            os.chdir(old_pwd)

        txt_a = [x+'\n' for x in 'abcdefghijklmnop']
        txt_b = [x+'\n' for x in 'abcdefxydefghijklmnop']
        with open(os.path.join(self.test_dir, 'a2'), 'w') as f:
            f.writelines(txt_a)
        with open(os.path.join(self.test_dir, 'b2'), 'w') as f:
            f.writelines(txt_b)

        # This is the result with LongestCommonSubstring matching
        os.chdir(self.test_dir)
        try:
            self.assertEqual(['--- a2\n',
                              '+++ b2\n',
                              '@@ -1,6 +1,11 @@\n',
                              ' a\n',
                              ' b\n',
                              ' c\n',
                              '+d\n',
                              '+e\n',
                              '+f\n',
                              '+x\n',
                              '+y\n',
                              ' d\n',
                              ' e\n',
                              ' f\n'], list(unified_diff_files('a2', 'b2')))

            # And the patience diff
            self.assertEqual(['--- a2\n',
                              '+++ b2\n',
                              '@@ -4,6 +4,11 @@\n',
                              ' d\n',
                              ' e\n',
                              ' f\n',
                              '+x\n',
                              '+y\n',
                              '+d\n',
                              '+e\n',
                              '+f\n',
                              ' g\n',
                              ' h\n',
                              ' i\n'],
                             list(unified_diff_files('a2', 'b2',
                                                     sequencematcher=psm)))
        finally:
            os.chdir(old_pwd)


class TestPatienceDiffLibFiles_c(TestPatienceDiffLibFiles):

    def setUp(self):
        super(TestPatienceDiffLibFiles_c, self).setUp()
        try:
            from . import _patiencediff_c
        except ImportError:
            self.skipTest('C extension not built')
        self._PatienceSequenceMatcher = \
            _patiencediff_c.PatienceSequenceMatcher_c


class TestUsingCompiledIfAvailable(unittest.TestCase):

    def test_PatienceSequenceMatcher(self):
        try:
            from ._patiencediff_c import PatienceSequenceMatcher_c
        except ImportError:
            from ._patiencediff_py import PatienceSequenceMatcher_py
            self.assertIs(PatienceSequenceMatcher_py,
                          patiencediff.PatienceSequenceMatcher)
        else:
            self.assertIs(PatienceSequenceMatcher_c,
                          patiencediff.PatienceSequenceMatcher)

    def test_unique_lcs(self):
        try:
            from ._patiencediff_c import unique_lcs_c
        except ImportError:
            from ._patiencediff_py import unique_lcs_py
            self.assertIs(unique_lcs_py,
                          patiencediff.unique_lcs)
        else:
            self.assertIs(unique_lcs_c,
                          patiencediff.unique_lcs)

    def test_recurse_matches(self):
        try:
            from ._patiencediff_c import recurse_matches_c
        except ImportError:
            from ._patiencediff_py import recurse_matches_py
            self.assertIs(recurse_matches_py,
                          patiencediff.recurse_matches)
        else:
            self.assertIs(recurse_matches_c,
                          patiencediff.recurse_matches)
