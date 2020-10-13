from .pipeable import pipeable
import re


def split(pat):
    ''' creates a pipeable function that will split a string using a regular expression based on pat.
    
    args:
        pat: a regular expression pattern used to split strings.

    return:
        a list of strings, resulting from splitting s at each instance of sep.
        note that sep is removed in the process.

    notes:
        Call: 
            To provide efficient computation, split returns a pipeable function.
            To perform a regular call: split(pat)(s) 
            Use regular syntax for piping: or s >> split(pat)

        Partial application: 
            Is curried and can be combined with curried functions (i.e. map)
            Example: list_of_str >> composable.strict.map(split("(,|\t)"))
    '''
    r = re.compile(pat)
    return pipeable(lambda s: r.split(s))




def search(pat):
    ''' creates a pipeable function that will search a string for a regular expression pattern, 
    matching the first instance.
    
    args:
        pat: a regular expression pattern 

    return:
        an re.match object if a match was found, or None if not.

    notes:
        Call: 
            To provide efficient computation, search precompiles the pattern 
            then returns a pipeable function.
            To perform a regular call: search(pat)(s) 
            Use regular syntax for piping: or s >> search(pat)

        Partial application: 
            Is curried and can be combined with curried functions (i.e. map)
            Example: list_of_str >> composable.strict.map(search("(,|\t)"))
    '''
    r = re.compile(pat)
    return pipeable(lambda s: r.search(s))


def match(pat):
    ''' creates a pipeable function that check of the start of a string matches the regular expression pattern, 
    
    args:
        pat: a regular expression pattern

    return:
        an re.match object if a match was found, or None if not.

    notes:
        Call: 
            To provide efficient computation, match precompiles the pattern 
            then returns a pipeable function.
            To perform a regular call: match(pat)(s) 
            Use regular syntax for piping: or s >> match(pat)

        Partial application: 
            Is curried and can be combined with curried functions (i.e. map)
            Example: list_of_str >> composable.strict.map(match("(,|\t)"))
    '''
    r = re.compile(pat)
    return pipeable(lambda s: r.match(s))


def _is_result(r):
    ''' Check to see if a value is either an instance of re.Match or None '''
    return isinstance(r, re.Match) or r is None


def groups(match_result, default=None):
    ''' creates a pipeable function that calls the groups method on a match object, 
    or returns None if there is no match
    
    args:
        pat: the result of a regular expression match/search.  Can be an instance of re.Match or None

    return:
        a tuple of capture groups or, in the case of None, an empty tuple.

    notes:
        Piping: 
            Is curried and can be combined with curried functions (i.e. map)
            Example: s >> composable.re.match("(,|\t)") >> groups()
    '''
    return match_result if isinstance(match_result, re.Match) else default


