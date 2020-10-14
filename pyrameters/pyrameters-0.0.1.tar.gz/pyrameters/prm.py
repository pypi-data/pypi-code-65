'''
Module for loading a Deal.II parameter file from a raw file or string input.
'''

import re
from .Subsection import Subsection

class PRM(Subsection):
    '''
    This class represents a complete parameter file, including both global
    options and subsections. It is effectively just a Subsection object with
    no 'parent', and contains a parser function to read parameters from input.
    '''
    def __init__ (self, input=None):
        super().__init__(name='/', parent=None)
        if input is not None:
            self.parse(input)

    def __str__ (self):
        # Return a string representation of this parameter file. Note that
        # comments in the original input file will be lost, and the contents
        # may be in a different order than the input.
        return Subsection.str_helper(self).strip()

    def parse (self, input):
        self.raw = input.replace('\r\n','\n')
        # Strip single-line comments
        prm_text = re.sub(r'\#.*$', '', self.raw, flags=re.MULTILINE)
        # Line continuations (concatenate lines ending with \ with next line)
        prm_text = re.sub(r'\s*\\\s*\n\s*', ' ', prm_text, flags=re.MULTILINE)
        prm_lines = [s.strip() for s in prm_text.split('\n')]

        optionregex = re.compile(r'^\s*set ([^=]*)\s*=\s*(.*)\s*$')
        subsectionregex = re.compile(r'^subsection (.*)$')

        branch = self
        for line in prm_lines:
            optmatch = optionregex.search(line)
            if optmatch:
                option,valstr = [s.strip() for s in optmatch.groups()]
                if option in branch:
                    sys.stderr.write('Warning: Option redefined')
                    sys.stderr.write(' <%s%s>\n'%(branch.get_path(),option))
                    sys.stderr.flush()
                branch[option] = Subsection.auto_cast(valstr)
                continue
            subsectionmatch = subsectionregex.search(line)
            if subsectionmatch:
                name = subsectionmatch.groups()[0]
                if name in branch:
                    sys.stderr.write('Warning: Subsection redefined')
                    sys.stderr.write(' <%s%s/>\n'%(branch.get_path(),name))
                    sys.stderr.flush()
                branch[name] = Subsection(name, branch)
                branch = branch[name]
                continue
            if line == 'end':
                branch = branch.parent
                assert branch is not None, \
                    'Invalid parameter file. Unmatched subsection end.'
                continue
            assert line == '', 'Parameter line unrecognized <%s>'%line
        assert branch is self, \
            'Invalid parameter file: Unmatched subsection opening.'
