"""Class for generate logic express"""


class Logic:
    """Convert express to Logic object"""

    def __init__(self, term):
        if isinstance(term, str):
            self._value = term
        elif isinstance(term, bytes):
            self._value = str(term, 'utf8')
        else:
            self._value = str(term)

    def __eq__(self, item):
        return self._value == str(item)

    def __or__(self, term):
        """use `|` to act OR"""
        return OR(self, term)

    def __and__(self, term):
        """use `&` to act AND"""
        return AND(self, term)

    def __str__(self):
        return self._value

    def __repr__(self):
        return f'Logic({self})'


# Alias for Logic
L = Logic


class ComplexLogicBase(Logic):

    def __init__(self, term_1, term_2, **terms):

        self._terms = []

        self._add(term_1)
        self._add(term_2)

        for term in terms:
            self._add(term)

        t_list = []

        for t in self:
            if isinstance(t, ComplexLogicBase):
                t_str = f'({t})'
            else:
                t_str = f'{t}'
            t_list.append(t_str)
        oper = f' {self.__class__.__name__} '
        self._value = oper.join(t_list)

    def __iter__(self):
        return iter(self._terms)

    def __len__(self):
        return len(self._terms)

    def __getitem__(self, key):
        return self._terms[key]

    def _add(self, term):
        if term not in self:
            if isinstance(term, Logic):
                if isinstance(term, self.__class__):
                    for t in term:
                        self._terms.append(t)
                else:
                    self._terms.append(term)
            else:
                self._terms.append(Logic(term))

    def __repr__(self):
        term_list = [repr(c) for c in self]
        v = ','.join(term_list)
        return f'{self.__class__.__name__}({v})'


class AND(ComplexLogicBase):
    """Logic AND"""


class OR(ComplexLogicBase):
    """Logic OR"""
