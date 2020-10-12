import sys

def default_on_error(question, choices, default, error):
    '''
    A default callback after failed validation of the answer
    '''
    sys.stderr.write('%s\n'%error)

def default_on_success(question, answer):
    '''
    A default callback after successful validation of the answer
    '''
    sys.stdout.write('%s\n'%answer)