from datetime import date, datetime
try:
    from cerberus import Validator as ValidatorCerberus
except ImportError:
    raise ImportError('Cerberus not installed')


class BaseValidator(ValidatorCerberus):

    def _validate_no_spaces(self, no_spaces, field, value):
        """ Test the value must not contain spaces

        The rule's arguments are validated against this schema:
        {'type': 'boolean'}
        """
        if no_spaces and (' ' in value):
            self._error(field, "Must not contain spaces")

    def _validate_only_numbers(self, only_numbers, field, value):
        """ Test only numbers of a value.

        The rule's arguments are validated against this schema:
        {'type': 'boolean'}
        """

        if (
            only_numbers and value != '' and
            value is not None and
            not value.isdigit()
        ):
            self._error(field, "Only numeric digits is allowed")

    def _normalize_coerce_date(self, value):
        """Normalize a date, if it comes as str converts it to datetime.date.
        """
        if isinstance(value, str):
            return datetime.strptime(value, '%Y-%m-%d').date()
        if isinstance(value, date):
            return value
        return value

    def _validate_multiple(self, multiple_value, field, value):
        """ {'nullable': False } """
        try:
            if value % multiple_value != 0:
                self._error(field, f'is not a multiple of {multiple_value}')
        except TypeError:
            pass
