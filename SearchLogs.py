#!/usr/bin/env python

###############################################################################
# A log search utility.                                                       #
# Includes some advanced options, including ranges, ORs, less than            #
# and greater than.                                                           #
#                                                                             #
# options: i (ignore case)                                                    #
#          w (ignore whitespace)                                              #
#                                                                             #
#                                                                             #
# ranges: A single number for an exact number of matches     ex: 1            #
#         A dash in between numbers for a range of matches   ex: 2-4          #
#         A pipe in between numbers for a match of either    ex: 1|3          #
#         A plus sign for at least that many matches         ex: 5+           #
#         A minus sign for at most that many matches         ex: 5-           #
#         A zero indicates the line should not appear        ex: 0            #
#                                                                             #
# A test case file should be in the form:                                     #
#      <options>:<occurrences>:<logfile>:<string>                             #
# However, <options> may be empty if none are used. Still need a :            #
#                                                                             #
# Intended for use with python 2.6 and 2.7                                    #
#                                                                             #
# Author: Seth Hoenig 2013                                                    #
###############################################################################

from __future__ import print_function
from __future__ import with_statement

import optparse
import sys
import os
import re

TRACE=None

def log(msg):
    if TRACE:
        print(msg, file=TRACE)

TEST_RE = re.compile('''
              ([iw]*)                                # Options
              :
              ([\d]+ | [\d]+[+-] | [\d]+[\|-][\d]+)  # Value, Min/Max, Range/Or
              :
              ([^:\s]+)                              # Filename
              :
              (.+)                                   # Text
              '''
             , re.DOTALL | re.VERBOSE)

def parse_test(line):
    '''
    Parse a single test case out of a string using the TEST_RE regex
    up above to do the dirty work.
    line -- the raw string which contains the test case
    Return a dictionary of the form:
    { 'options' : <options>,
      'occurs'  : <occurences>,
      'logfile' : <the log file to search>,
      'string'  : <the string to search for> }
    '''
    m = TEST_RE.match(line.strip())
    if m is None:
        log('Invalid Test %s' % line)
        raise Exception('Invalid Test %s' % line)
    test = {'options': m.group(1),
            'occurs':  m.group(2),
            'logfile': m.group(3),
            'string':  m.group(4)}
    return test


def parse_comparetest_file(ifname):
    '''
    Parse the .comparetest file which should look something like,
       <options>:<occurrences>:<logfile>:<string>
    Each option is just a single character, which should be concatenated together
    Occurences can be a single number, a range, or a set of numbers divided by
    '|' to indicate an OR.
    This function parses the .comparetest file and returns a list of dicts,
    each describing a test. For example, [ {'options':'ix',
                                            'occurs':'1|3',
                                            'logfile':'filename.txt',
                                            'string':'foo bar baz!'}, ]
    ifname -- The input file name containing test case definitions
    '''
    tests = []
    try:
        with open(ifname, 'r') as infile:
            for line in infile.readlines():
                line = line.strip()
                if line=='' or line[0]=='#':
                    continue
                gs = parse_test(line)
                tests += [gs]
    except Exception as e:  
        log('Error reading comparetest file')
        log(str(e))
        sys.exit(1)
    return tests
    
def build_re(options, string):
    '''
    Build the final regex to search for, modifying according to
    options.
    options -- '', 'i', 'w', 'iw' are currently supported.
              i - ignore case
              w - ignore whitespace
    Returns the compiled regex ready to use (find, search, etc.)
    '''
    if 'w' in options:
        string = string.replace(' ',    '[\s]*')
        string = string.replace('\t',   '[\s]*')
        string = string.replace('\n',   '[\s]*')
        string = string.replace('\r\n', '[\s]*')
    if 'i' in options:
        return re.compile(string, re.IGNORECASE)
    else:
        return re.compile(string)


def parse_range(test):
    '''
    Parse the range condition of a test case.
    test -- the test case which contains a string description of the
    range validation.
    Return ('range',   low, high)  for a range between low and high
           ('or',      a, b)  for one of A or B
           ('value',   n)     for exactly N matches
           ('atleast', n)     for at least N matches
           ('atmost',  n)     for at most N matches
    '''
    x = test['occurs']
    if '-' in x:
        sp = x.split('-')
        if sp[1]:
            a, b = int(sp[0]), int(sp[1])
            if a > b:
                a, b = b, a
            return ('range', a, b)
        else:
            return ('atmost', int(sp[0]))
    elif '|' in x:
        sp = x.split('|')
        return ('or', int(sp[0]), int(sp[1]))
    elif '+' in x:
        sp = x.split('+')
        return ('atleast', int(sp[0]))
    else:
        return ('value', int(x))

def verify_in_range(n, allowed):
    '''
    Checks to see if n is accepted by the range of the test case.
    n -- the actual number of occurences of a string found
    allowed -- a tuple of two or three arguments, first is one of,
    'atmost', 'atleast', 'or', 'value', 'range'. The remaining arguments
    are values or bounds to which n is compared.
    '''
    t = allowed[0]
    a = int(allowed[1])
    if len(allowed) > 2:
        b = int(allowed[2])

    if t == 'atmost':
        return n <= a
    elif t == 'range':
        return n >= a and n <= b
    elif t == 'or':
        return n == a or n == b
    elif t == 'atleast':
        return n >= a
    else: # t == 'value'
        return n == a


def run_test(test):
    '''
    Runs a single test case.
    test -- A dict containing options, occurs, logfile, and string
    Returns a tuple of two arguments, True or False if the test passed
    or failed, followed by an error string if any.
    '''
    with open(test['logfile'], 'r') as f:
        content = f.read()
        r = build_re(test['options'], test['string'])
        n = len(r.findall(content))
        rng = parse_range(test)
        if verify_in_range(n, rng):
            return (True, '')
        else:
            return (False, 'not in range') # todo give better error

##############
# Start Here #
##############
if __name__ == '__main__':
    parser = optparse.OptionParser()
    parser.add_option('-i', '--input', dest='inputfilename',
              default=None, action='store', type='string',
              help='The .comparetest file containing lines to search for')
    parser.add_option('-o', '--output', dest='logfilename',
              default=None, action='store', type='string',
              help='Send output of searchLogs.py to specified file')
    
    (options, args) = parser.parse_args()

    if options.logfilename:
        if options.logfilename == 'stdout':
            TRACE=sys.stdout
        elif options.logfilename == 'stderr':
            TRACE = sys.stderr
        else:
            TRACE = open(options.logfilename, 'w')
    else:
        TRACE=sys.stdout
    
    log('-- SearchLogs.py --')
    
    if not options.inputfilename:
        log('compare test file must be specified with -i <file>')
        sys.exit(1)
    
    tests = parse_comparetest_file(options.inputfilename)
    
    overall = True
    
    for test in tests:
        result = run_test(test)
        if not result[0]:
            overall = False
            log('Failed test, %r' % test)
            
    if overall:
        log('PASSED')
        

