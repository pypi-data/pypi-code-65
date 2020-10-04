from expression.src.condition import Condition, Conjunction
from expression.src.expression import Expression


class NoHandlerFound(Exception):
    pass


class Evaluate():

    def __init__(self, data = {}):
        self._data = data
        self._condition_handlers = {}

    def add_condition_handlers(self, condition_handlers):
        for i in condition_handlers:
            self._condition_handlers[i] = condition_handlers[i]

    def from_expression(self, expression):
        conditions = Expression(expression).to_conditions()

        return self.from_conditions(conditions.conditions)

    def from_conditions(self, conditions):
        return eval(self._resolve_conditions(conditions))

    def _resolve_conditions(self, conditions):
        store = ''
        for condition in conditions:

            if isinstance(condition, list):
                store += '({})'.format(self._resolve_conditions(condition))
            elif isinstance(condition, Condition):
                store += '{}'.format(self._resolve_condition(condition))
            elif isinstance(condition, Conjunction):
                store += ' {} '.format(condition.value)

        return store

    def _resolve_condition(self, condition):

        if condition.operator not in self._condition_handlers:
            raise NoHandlerFound

        handler = self._condition_handlers[condition.operator]
        return handler(self._data).handle(condition)
