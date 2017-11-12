
import re
import unittest

from regroup import match, DAWG


class TestParens(unittest.TestCase):

    def test_empty(self):
        strings = ['', 'aa', 'bb']
        self.assertEqual('(aa|bb)?', match(strings))

    def test_parens(self):
        strings = ['aa', 'bb', 'c']
        self.assertEqual('(aa|bb|c)', match(strings))

    def test_parens2(self):
        strings = ['aa', 'ab', 'bb']
        # dawg = DAWG.from_list(strings)
        # print(dawg)
        # [ab][ab]
        # (a[ab]|bb)
        self.assertEqual('(a[ab]|bb)', match(strings))

    def test_parens3(self):
        strings = ['aaa', 'abb', 'c']
        self.assertEqual('(a(aa|bb)|c)', match(strings))

    def test_parens4(self):
        strings = ['aaa', 'abb', 'cc', 'dd']
        self.assertEqual('(a(aa|bb)|cc|dd)', match(strings))

    def test_greenred(self):
        strings = ['Black', 'Blue', 'Green', 'Red']
        self.assertEqual('(Bl(ack|ue)|Green|Red)', match(strings))

    @unittest.expectedFailure
    def test_bat_brat_cat(self):
        strings = ['bat', 'brat', 'cat']
        # FIXME: our crappy DAWG doesn't merge suffixes for strings that don't start the same...
        # dawg = DAWG.from_iter(strings)
        # print(dawg)
        self.assertEqual('(br?|c)at', match(strings))
        # current result:
        # self.assertEqual('(br?at|cat)', match(strings))

    def test_tap_taps_top_tops(self):
        strings = ['tap', 'taps', 'top', 'tops']
        self.assertEqual('t[ao]ps?', match(strings))

    def test_shared_suffix_abcdef_def(self):
        strings = ['abcdef', 'def']
        self.assertEqual('(abc)?def', match(strings))

    def test_optional_space(self):
        self.assertEqual('a( b)?', match(['a', 'a b']))

    def test_optional_group_complex(self):
        # joe(s(eph)?|y?)  # technically accurate, as "y" is optional
        # joe(s(eph)?|y)?  # ...better, i think
        self.assertEqual('joe(s(eph)?|y?)', match(['joe', 'joey', 'joes', 'joeseph']))

"""
class TestDAWG(unittest.TestCase):

    '''
    test internal DAWG implementation
    '''

    def test_dawg1(self):
        self.assertEqual(dawg({'2': {'3': {'': {}}}}),
                         {'23': {'': {}}})

        self.assertEqual(DAWG({'2': {'3': {'': {}}}}),
                         {'23': {'': {}}})

    def test_dawg2(self):
        self.assertEqual(dawg_make({'1': {'2': {'3': {'': {}}}}}),
                         {'123': {'': {}}})

    def test_dawg3(self):
        self.assertEqual(dawg_make({'1': {'2': {
                                    '3': {'': {}},
                                    '4': {'': {}}}}}),
                         {'12': {'3': {'': {}},
                                 '4': {'': {}}}})

    def test_dawg4(self):
        '''multiple items under 1, '3' is condensed'''
        self.assertEqual(dawg_make({'1': {'2': {'': {}},
                                          '3': {'4': {'': {}}}}}),
                         {'1': {'2': {'': {}},
                                '34': {'': {}}}})

    def test_flatten(self):
        self.assertEqual(['ab', 'cb'],
                         list(dawg_flatten(dawg_make(trie_make(['ab', 'cb'])))))
"""


class TestDigits(unittest.TestCase):

    '''
    Test common numerical patterns
    '''

    def test_empty(self):
        self.assertEqual('', match([]))

    def test_1(self):
        self.assertEqual('0', match(['0']))

    def test_dupes(self):
        self.assertEqual('0', match(['0', '0']))

    def test_01(self):
        self.assertEqual('(00|11)', match(['00', '11']))

    def test_0_1(self):
        self.assertEqual('(0 0|1 1)', match(['0 0', '1 1']))

    def test_float_maybe_dot(self):
        # self.assertEqual('([0-9]|[0-9]\.)', match(['0', '0.']))
        self.assertEqual('0\.?', match(['0', '0.']))

    def test_float_maybe_(self):
        # self.assertEqual('([0-9]|[0-9]\.[0-9])',
        #                match(['0', '0.1']))
        self.assertEqual('0(\.1)?',
                         match(['0', '0.1']))

    def test_float_variable_prefix(self):
        self.assertEqual('0(.12?)?',
                         match(['0', '0.1', '0.12']))

    def test_float_variable_prefix23(self):
        # 0(|.1(|23))
        # 0(.1(23)?)?
        self.assertEqual('0(.1(23)?)?',
                         match(['0', '0.1', '0.123']))

    def test_numbers(self):
        # (100?|[1-9]|)|[2-9][0-9]?|0
        # (0|(1(|00?|[1-9]))|[2-9][0-9]?)
        # (0|(1(|00?|[1-9]))|[2-9][0-9]?)

        # (100?|[1-9]|)|[02-9][0-9]?
        # (100|[0-9][0-9]?)
        # (1?[0-9][0-9]?)  XXX: too broad
        vals = [str(n) for n in range(101)]
        pattern = match(vals)
        fullpat = '^({})$'.format(pattern)
        self.assertTrue(all(re.match(fullpat, v) for v in vals))
        self.assertEqual('(0|1(00?|[1-9]?)|[2-9][0-9]?)', pattern)

    def test_hundreds(self):
        '''test that shared suffixes are combined even when first char differs...'''
        # TODO: combining shared suffixes does not work if beginning is different
        self.assertEqual('[12]00',
                         match(['100', '200']))

    def test_100_101(self):
        self.assertEqual('10[01]',
                         match(['100', '101']))


class TestEFGreen(unittest.TestCase):

    '''
    Test real-world problem
    '''

    # ref: http://stackoverflow.com/questions/1410822/how-can-i-detect-common-substrings-in-a-list-of-strings
    strings = [
        'EFgreen',
        'EFgrey',
        'EntireS1',
        'EntireS2',
        'J27RedP1',
        'J27GreenP1',
        'J27RedP2',
        'J27GreenP2',
        'JournalP1Black',
        'JournalP1Blue',
        'JournalP1Green',
        'JournalP1Red',
        'JournalP2Black',
        'JournalP2Blue',
        'JournalP2Green'
    ]

    def test_pattern_match(self):
        dawg = DAWG.from_list(self.strings)
        pattern = dawg.serialize()
        dont_match = [s for s in self.strings
                      if not re.match('^' + pattern + '$', s)]
        self.assertEqual([], dont_match)

    def test_pattern(self):
        self.assertEqual(
            match(self.strings),
            '(E(Fgre(en|y)|ntireS[12])|J(27(Green|Red)P[12]|ournalP(1(Bl(ack|ue)|(Green|Red))|2(Bl(ack|ue)|Green))))')

    def test_cluster(self):
        dawg = DAWG.from_list(self.strings)
        clusters = dawg.cluster_by_prefixlen(2)
        cluster_strings = [prefix + DAWG._serialize(suffix_tree)
                           for prefix, suffix_tree in clusters]
        self.assertEqual(
            cluster_strings,
            ['EFgre(en|y)',
             'EntireS[12]',
             'J27(Green|Red)P[12]',
             'JournalP(1(Bl(ack|ue)|(Green|Red))|2(Bl(ack|ue)|Green))'])

    def test_cluster_prefixlen_tooshort(self):
        '''
        ensure that when clustering by prefixlen, any patterns shorter than the specified length are included in the results
        '''
        dawg = DAWG.from_list(['abc', 'abcde'])
        clusters = dawg.cluster_by_prefixlen(4)  # longer than len('abc')
        cluster_strings = [prefix + DAWG._serialize(suffix_tree)
                           for prefix, suffix_tree in clusters]
        self.assertEqual(cluster_strings, ['abc', 'abcde'])
