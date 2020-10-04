import re
from expression.src.condition import Conditions, ConditionSerializer, Conjunction
from expression.src.enclosure import Boundary, ResolveEnclosureGroups


class ExpressionBadlyTerminated(Exception):
    pass


class ExpressionBadlyFormatted(Exception):
    pass


class Expression():

    CONJUNCTIONS = [
        'and',
        'or'
    ]

    REPLACEMENT_RULES = {
        r'\s+': ' ',
        r'[\s]+': ' ',
        r'\s?\(\s?': '(',
        r'\s?\)\s?': ')',
        r'\s?([\,\:])\s?': ','
    }

    condition_count = 0
    operator_count = 0

    def __init__(self, expression):
        self.expression = expression

    def to_conditions(self):
        conditions = self._generate_conditions(self.expression)
        if self.condition_count and self.condition_count - 1 != self.operator_count:
            raise ExpressionBadlyFormatted

        return Conditions(conditions)

    def _is_enclosed(self, expression):

        return expression[0] == Boundary.OPENING \
            and expression[-1] == Boundary.CLOSING

    def _resolve_conditions(self, conditions):
        store = []
        for condition in conditions.values():
            if condition not in self.CONJUNCTIONS:
                self.condition_count += 1
                store.append(ConditionSerializer().deserialize(condition))
            else:
                self.operator_count += 1
                store.append(Conjunction(condition))

        return store

    def _generate_conditions(self, expression):
        store = []
        for fragment in self._split_compound_expression_into_root_fragments(expression):
            if self._is_enclosed(fragment):
                conditions = self._generate_conditions(fragment)

                if len(conditions) > 0:
                    store.append(conditions)
            else:
                store = store + self._resolve_conditions(
                    self._resolve_statement_segments(fragment)
                )

        if len(store) > 0 and isinstance(store[-1], Conjunction):
            raise ExpressionBadlyTerminated

        return store

    def _split_compound_expression_into_root_fragments(self, expression):
        """Split compound expressions into root fragments.

        a = 1 and (b = 1 or c = 3) would be resolved to
        ['a = 1 and', '(b = 1 or c = 3)']
        """
        expression = self._normalise_expression(expression)
        expression = self._unwrap_expression(expression)
        groups = ResolveEnclosureGroups().from_expression(expression)

        length = len(expression)
        store = []
        i = 0

        while (i < length):
            closing_index = groups.get_closing_index(i)

            if closing_index is not None:
                fragment_end = closing_index + 1
                fragment = expression[i:fragment_end]
                store.append(fragment)
                groups.remove_groups_between(i, fragment_end)
                i = fragment_end - 1
            else:
                next_group_start_index = groups.get_first_group_index()
                next_group_start_index = next_group_start_index \
                    if next_group_start_index else length

                fragment = expression[i:next_group_start_index]
                store.append(fragment)
                i = next_group_start_index - 1

            i += 1

        return store

    def _resolve_statement_segments(self, expression):
        segments = expression.split(' ')
        statements = {}
        i = 0
        for segment in segments:
            if segment in self.CONJUNCTIONS:
                i += 1
                statements[i] = [segment]
                i += 1
            else:
                if i not in statements:
                    statements[i] = []
                statements[i].append(segment)

        return self._resolve_statements(statements)

    def _resolve_statements(self, statements):
        for i in statements:
            if len(statements[i]) == 1:
                statements[i] = ''.join(statements[i])
            else:
                statements[i] = ' '.join(statements[i])

        return statements

    def _normalise_expression(self, expression):
        for regex, replace in self.REPLACEMENT_RULES.items():
            expression = re.sub(regex, replace, expression)

        return expression.strip()

    def _unwrap_expression(self, expression):
        """Recursively un_wrap the expression.

        Ensure that ((((a + b)))) resolves to a + b.
        """
        groups = ResolveEnclosureGroups().from_expression(expression)
        un_wrap = True

        while (un_wrap):
            if groups.get_closing_index(0) == len(expression) - 1:
                expression = expression[1:-1]
                groups = ResolveEnclosureGroups().from_expression(expression)
                un_wrap = True
            else:
                un_wrap = False

        return expression
