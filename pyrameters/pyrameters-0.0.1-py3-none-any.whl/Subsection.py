'''
This class represents a parameter section. It inherits from dict, and stores
both options and subsections as key/value pairs.
'''
class Subsection(dict):
    def __init__ (self, name, parent=None):
        # Subsections have names (part of their logical path), and a reference
        # to their parent section. In the case of the global section, the parent
        # object is set to None.
        self.name = name
        self.parent = parent

    def add_subsection(self, section):
        if type(section) is str:
            self[section] = Subsection(section, self)
        elif type(section) is Subsection:
            section.parent = self
            self[section.name] = section
        else:
            assert False, 'Subsection must be a string or a subsection.'

    def get (self, path):
        # Get an option or subsection based on its relative path.
        path = [loc for loc in path.split('/') if len(loc) > 0]
        if len(path) == 0:
            return None
        subpath = path.pop(0)
        if not subpath in self:
            return None
        elif len(path) == 0:
            return self[subpath]
        else:
            return self[subpath].get('/'.join(path))

    def set (self, path, value):
        # Set an option based on its relative path. Missing subsections will be
        # created.
        path = [loc for loc in path.split('/') if len(loc) > 0]
        assert len(path) > 0, 'Invalid paramter path'
        subpath = path.pop(0)
        if len(path) == 0:
            if type(value) is int:
                value *= 1.0
            self[subpath] = value
        else:
            if not subpath in self.keys():
                self[subpath] = Subsection(subpath, self)
            assert type(self[subpath]) is Subsection, \
                'Invalid subsection (already defined as option)'
            self[subpath].set('/'.join(path), value)

    def get_path (self):
        # Recursively traverse *up* the options tree to determine the absolute
        # path of this subsection. Subsection paths always end with a '/'.
        if self.parent is None:
            return '/'
        else:
            return self.parent.get_path() + self.name + '/'

    def get_subsections (self):
        # Return a subset of the key/value pairs in this subsection that are
        # themselves subsections.
        return {k:v for k,v in self.items() if (type(v) is Subsection)}

    def get_options (self):
        # Return a subset of the key/value pairs in this subsection that are
        # leaf nodes (ordinary option values)
        return {k:v for k,v in self.items() if (type(v) is not Subsection)}

    @classmethod
    def str_helper (self, branch, indent=0):
        # return a pretty-print representation of a subsection branch, using a
        # specified indentation level.
        optstrs = []
        for k in sorted(branch.get_options(), key=(lambda s: s.lower())):
            v = branch[k]
            opt = Subsection.stringify_option(v)
            s1 = (' '*indent)+('set %s = '%k)
            optstrs.append(s1 + Subsection.wrap_line(opt, len(s1)))

        secstrs = []
        for k in sorted(branch.get_subsections(), key=(lambda s: s.lower())):
            secstrs.append(branch.str_helper(branch[k], indent+2))

        STR = ('\n\n'.join(['\n'.join(optstrs), '\n\n'.join(secstrs)])).strip()
        if branch.parent is None:
            return STR
        else:
            return (((' '*(indent-2))+'subsection '+branch.name+'\n') \
                    + (' '*(indent)) + STR \
                    + ('\n'+(' '*(indent-2))+'end'))

    @staticmethod
    def wrap_line (opt, indent, width=80):
        # deal.ii allows wrapping long lines by placing a backslash character at
        # the end of a line, and continuing its contents on the next line.
        # This function attempts to do that automatically, by splitting on
        # whitespace.
        ret = ''
        line = ''
        for token in opt.split(' '):
            if len(line) == 0:
                if len(ret) == 0:
                    line = ' '*indent
                line += token
            else:
                if len(line)+len(token)+2 > 80:
                    ret += ' ' + line + ' \\\n'
                    line = ' '*indent + token
                else:
                    line += ' '+token
        ret += line
        return ret.strip()

    @staticmethod
    def stringify_option (value):
        # Represent an option in prm file syntax. Numbers, lists, and booleans
        # all need to be specified in particular formats for deal.ii to recognize
        # them.
        if type(value) is str:
            return value
        elif type(value) is float or type(value) is int:
            return '%g'%value
        elif type(value) is list:
            return ', '.join([Subsection.stringify_option(v) for v in value])
        elif type(value) is dict:
            return ', '.join(['%s=%s'%(k,Subsection.stringify_option(v)) \
                                for k,v in value.items()])
        elif value == True:
            return 'true'
        elif value == False:
            return 'false'

    @staticmethod
    def auto_cast (value):
        # Without a schema to tell us about the structure of a paramter file
        # we need to guess option types. This function attempts to do that.
        value = value.strip()
        if value == 'true':
            return True
        elif value == 'false':
            return False
        elif value.count('=') == 1:
            k, v = value.split('=')
            return (k.strip(), Subsection.auto_cast(v))
        else:
            try:
                return float(value)
            except:
                # Is this a list of things?
                if ',' in value:
                    values = value.split(',')
                    # This might be an equation with commas in function calls,
                    # in which case we do not want to treat it as a list at all.
                    if all([s.count('(') == s.count(')') for s in values]):
                        rlist = [Subsection.auto_cast(v) for v in values]

                        if all([(type(item) is tuple) for item in rlist]):
                            # All list items are key=value pairs. We should
                            # return this as a dictionary rather than a list
                            rdict = {item[0]: item[1] for item in rlist}
                            # Check for duplicate key/value pairs
                            if len(rdict.keys()) == len(rlist):
                                return rdict
                        # Nope, just a regular old list.
                        return rlist

            # Fall back to just return this value as a single plain string
            return value
