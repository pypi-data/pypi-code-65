class Boundary():
    OPENING = '('
    CLOSING = ')'


class EnclosureGroups():

    def __init__(self):
        self._opening_indexes = []
        self._groups = {}

    def open_at(self, opening_index):
        self._opening_indexes.append(opening_index)
        self._groups[opening_index] = None

    def close_at(self, closing_index):
        opening_index = self._opening_indexes.pop()
        self._groups[opening_index] = closing_index

    def get_closing_index(self, opening_index):
        if opening_index in self._groups:
            return self._groups[opening_index]

        return None

    def get_first_group_index(self):
        if bool(self._groups) is True:
            return next(iter(self._groups))

        return None

    def _remove_group_by_opening_index(self, opening_index):
        if opening_index in self._groups:
            del self._groups[opening_index]

    def remove_groups_between(self, opening_index, closing_index):
        index_range = range(opening_index, closing_index)
        for i in index_range:
            self._remove_group_by_opening_index(i)


class ResolveEnclosureGroups():

    def from_expression(self, expression):
        groups = EnclosureGroups()

        for i in range(len(expression)):
            if Boundary.OPENING == expression[i]:
                groups.open_at(i)
            elif Boundary.CLOSING == expression[i]:
                groups.close_at(i)

        return groups
