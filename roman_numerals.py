#!/usr/bin/env python
"""
A function which returns a Roman numeral string representation of a given 
Arabic number.
"""


examples = { 4: 'IV', 1903:'MCMIII', 1:'I', 2:'II', 3:'III', 100: 'C',
            45:'XLV', 1954: 'MCMLIV', 1990: 'MCMXC', 2014: 'MMXIV', 22:'XXII'}

def test():
    '''Assert that the function roman_numeral conforms to the known examples.'''
    for arabic_number_, roman_numeral_ in examples.iteritems():
        assert( roman_numeral( arabic_number_) == roman_numeral_ )
    print 'All known roman numerals were successfully reproduced.'


# structered table of roman number symbols
# first level: power of ten
# second level: symbols for that power of ten
symbols = { 0: ('I','V'),
            1: ('X','L'),
            2: ('C','D'),
            3: ('M')     }
# since the symbol list is finite, there is a largest number that can be
# represented given the symbol list. In this case it is:
symbols_limit = 3999


# tools to compose roman numbers
def __subtract_small_symbol__( roman_number, power_of_ten ):
    return symbols[power_of_ten][0] + roman_number
    
def __add__small_symbol__( roman_number, power_of_ten ):
    return roman_number + symbols[power_of_ten][0]

def __get_symbol__( digit, power_of_ten ):
    '''Returns the Roman symbol to represent a given digit of certain order of
    magnitude (power of ten). The same rules apply for every power of ten, as
    specified by the cases below.'''
    if digit <= 3:
        ret = ''
        i = 0
        while i < digit:
            ret = __add__small_symbol__( ret, power_of_ten )
            i += 1
    elif digit == 4:
        ret = symbols[power_of_ten][1]
        ret = __subtract_small_symbol__( ret, power_of_ten )
    elif digit >= 5 and digit < 9:
        ret = symbols[power_of_ten][1]
        i = 0
        while i < digit-5:
            ret = __add__small_symbol__( ret, power_of_ten )
            i += 1
    elif digit == 9:
        ret = symbols[power_of_ten+1][0]
        ret = __subtract_small_symbol__( ret, power_of_ten )
    else:
        # digit has to match one of the above cases
        assert( False )
    return ret


def roman_numeral( arabic_number ):
    '''Main function. Returns a Roman numeral string representation of a given
    Arabic number.'''
    assert( type(arabic_number)==int and arabic_number>=0)
    assert( arabic_number <= symbols_limit )
    arabic_number_str = str( arabic_number )
    n_digits = len( arabic_number_str )
    roman_number = ''
    # Build the Roman numeral string back to front, starting with the lowest
    # power of ten, working up, prepending symbols to the string.
    for power_of_ten in range(n_digits):
        digit = int( arabic_number_str[n_digits - 1 - power_of_ten] )
        roman_number =  __get_symbol__(digit, power_of_ten) + roman_number
    return roman_number


# if executed, run the test function.
if __name__ == '__main__':
    test()
