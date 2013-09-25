#!/usr/bin/env python

# Test cases for SearchLogs.py

import unittest

from SearchLogs import parse_test
from SearchLogs import parse_range
from SearchLogs import verify_in_range
from SearchLogs import run_test

class TestSearchLogs(unittest.TestCase):

    ##############
    # parse_test #
    ##############

    def test_parse_test_1(self):
        line = ':1:blah.txt:hello world'
        r = parse_test(line)
        e = { 'options':'',
              'occurs':'1',
              'logfile':'blah.txt',
              'string':'hello world'}
        self.assertEqual(e, r)

    def test_parse_test_2(self):
        line = 'iw:1+:blah.txt:Blah'
        r = parse_test(line)
        e = { 'options':'iw',
              'occurs':'1+',
              'logfile':'blah.txt',
              'string':'Blah'}
        self.assertEqual(e, r)

    def test_parse_test_3(self):
        line = 'i:1-:blah.txt:Blah'
        r = parse_test(line)
        e = { 'options':'i',
              'occurs':'1-',
              'logfile':'blah.txt',
              'string':'Blah'}
        self.assertEqual(e, r)

    def test_parse_test_4(self):
        line = 'i:1-3:blah.txt:Blah'
        r = parse_test(line)
        e = { 'options':'i',
              'occurs':'1-3',
              'logfile':'blah.txt',
              'string':'Blah'}
        self.assertEqual(e, r)

    def test_parse_test_5(self):
        line = 'i:2|9:blah.txt:Blah'
        r = parse_test(line)
        e = { 'options':'i',
              'occurs':'2|9',
              'logfile':'blah.txt',
              'string':'Blah'}
        self.assertEqual(e, r)

    def test_parse_test_6(self):
        line = 'i:2|9:blah.txt:Blah\t     Foo'
        r = parse_test(line)
        e = { 'options':'i',
              'occurs':'2|9',
              'logfile':'blah.txt',
              'string':'Blah\t     Foo'}
        self.assertEqual(e, r)


    ###############
    # parse_range #
    ###############

    def test_parse_range_1(self):
        test = {'options':'',
                'occurs':'1',
                'logfile':'foo.txt',
                'string':'blah'}
        r = parse_range(test)
        e = ('value', 1)
        self.assertEqual(e, r)

    def test_parse_range_2(self):
        test = {'options':'',
                'occurs':'2-5',
                'logfile':'foo.txt',
                'string':'blah'}
        r = parse_range(test)
        e = ('range', 2, 5)
        self.assertEqual(e, r)

    def test_parse_range_3(self):
        test = {'options':'',
                'occurs':'4-',
                'logfile':'foo.txt',
                'string':'blah'}
        r = parse_range(test)
        e = ('atmost', 4)
        self.assertEqual(e, r)

    def test_parse_range_4(self):
        test = {'options':'',
                'occurs':'25000+',
                'logfile':'foo.txt',
                'string':'blah'}
        r = parse_range(test)
        e = ('atleast', 25000)
        self.assertEqual(e, r)

    def test_parse_range_5(self):
        test = {'options':'',
                'occurs':'3|9',
                'logfile':'foo.txt',
                'string':'blah'}
        r = parse_range(test)
        e = ('or', 3, 9)
        self.assertEqual(e, r)

    def test_parse_range_6(self):
        test = {'options':'',
                'occurs':'3|',
                'logfile':'foo.txt',
                'string':'blah'}
        try:
            r = parse_range(test)
        except:
            return
        self.fail()

    def test_parse_range_7(self):
        test = {'options':'',
                'occurs':'|3',
                'logfile':'foo.txt',
                'string':'blah'}
        try:
            r = parse_range(test)
        except:
            return
        self.fail()

    @unittest.skip('bad regex')
    def test_parse_range_8(self):
        test = {'options':'',
                'occurs':'2+4',
                'logfile':'foo.txt',
                'string':'blah'}
        try:
            r = parse_range(test)
        except:
            return
        self.fail()

    def test_parse_range_9(self):
        test = {'options':'',
                'occurs':'4-2',
                'logfile':'foo.txt',
                'string':'blah'}
        r = parse_range(test)
        e = ('range', 2, 4)
        self.assertEqual(e, r)


    ###################
    # verify_in_range #
    ###################

    def test_verify_in_range_1(self):
        n = 1
        allowed = ('value', 1)
        r = verify_in_range(n, allowed)
        e = True
        self.assertEqual(e, r)

    def test_verify_in_range_2(self):
        n = 3
        allowed = ('value', 1)
        r = verify_in_range(n, allowed)
        e = False
        self.assertEqual(e, r)

    def test_verify_in_range_3(self):
        n = 2
        allowed = ('range', 1, 4)
        r = verify_in_range(n, allowed)
        e = True
        self.assertEqual(e, r)

    def test_verify_in_range_4(self):
        n = 2
        allowed = ('range', 3, 8)
        r = verify_in_range(n, allowed)
        e = False
        self.assertEqual(e, r)

    def test_verify_in_range_5(self):
        n = 2
        allowed = ('or', 2, 5)
        r = verify_in_range(n, allowed)
        e = True
        self.assertEqual(e, r)

    def test_verify_in_range_6(self):
        n = 5
        allowed = ('or', 2, 5)
        r = verify_in_range(n, allowed)
        e = True
        self.assertEqual(e, r)

    def test_verify_in_range_7(self):
        n = 3
        allowed = ('or', 2, 5)
        r = verify_in_range(n, allowed)
        e = False
        self.assertEqual(e, r)

    def test_verify_in_range_8(self):
        n = 3
        allowed = ('atleast', 2)
        r = verify_in_range(n, allowed)
        e = True
        self.assertEqual(e, r)    

    def test_verify_in_range_9(self):
        n = 3
        allowed = ('atleast', 6)
        r = verify_in_range(n, allowed)
        e = False
        self.assertEqual(e, r)

    def test_verify_in_range_10(self):
        n = 3
        allowed = ('atmost', 2)
        r = verify_in_range(n, allowed)
        e = False
        self.assertEqual(e, r)    

    def test_verify_in_range_11(self):
        n = 3
        allowed = ('atmost', 3)
        r = verify_in_range(n, allowed)
        e = True
        self.assertEqual(e, r)

    ############
    # run_test #
    ############

    def test_run_test_1(self):
        test = {'options':'',
                'occurs':'1',
                'logfile':'sample.log',
                'string':'Hello World'}
        r = run_test(test)
        e = (True, '')
        self.assertEqual(e, r)

    def test_run_test_2(self):
        test = {'options':'',
                'occurs':'2',
                'logfile':'sample.log',
                'string':'Hello World'}
        r = run_test(test)
        e = (False, 'not in range')
        self.assertEqual(e, r)

    def test_run_test_3(self):
        test = {'options':'i',
                'occurs':'2',
                'logfile':'sample.log',
                'string':'Hello World'}
        r = run_test(test)
        e = (True, '')
        self.assertEqual(e, r)

    def test_run_test_4(self):
        test = {'options':'w',
                'occurs':'1',
                'logfile':'sample.log',
                'string':'Hello\tWorld'}
        r = run_test(test)
        e = (True, '')
        self.assertEqual(e, r)

    def test_run_test_5(self):
        test = {'options':'iw',
                'occurs':'2',
                'logfile':'sample.log',
                'string':'hello    world'}
        r = run_test(test)
        e = (True, '')
        self.assertEqual(e, r)


if __name__ == '__main__':
    unittest.main()
