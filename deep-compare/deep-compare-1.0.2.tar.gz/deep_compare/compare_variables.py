from datetime import datetime, date

from ast import literal_eval


class CompareVariables:
    """
    A class to compare variables with different datatypes
    ...

    Methods
    -------
    is_float(value):
        returns True if the value is an integer or float.

    is_date_time(value):
        returns True if value is a date or date-time.

    can_literal_eval(value):
        returns True if value is a list, dict, tuple, set etc.

    is_complex(value):
        returns True if value is a complex number.

    compare(value1, value2):
        returns True if the values are equal.

    compare_date(value1, value2):
        returns True if the input two input date values(value can be iso time format string also) are equal.

    compare_datetime(value1, value2):
        returns True if the two input datetime values(value can be iso time format string also) are equal.

    datatype_check(value):
        returns the input value in its correct datatype.

    compare_list_or_tuples_or_set(value1, value2):
        returns True if the input values(list/tuple/set) are equal.

    compare_dicts(value1, value2):
        returns True if the input values(dicts) are equal.

    type_matching_and_compare(value1, value2):
        returns True if the values are equal irrespective of the input datatype.
        
    """

    @staticmethod
    def is_float(value):
        '''This function checks if the input value is an integer or not and returns True or False.
        @params value: Input value to check
        @return Boolean: True if value is an integer or float'''

        try:
            float(value)
            return True
        except ValueError:
            return False
        except TypeError:
            return False
        except AttributeError:
            return False

    @staticmethod
    def is_date_time(value):
        '''This function checks if the input value is a datetime field or not and returns True or False.
        If the input value is in string format make sure it is in iso time format and python3.7 or above version is used.
        @params value: Input value to check
        @return Boolean: True if value is a date or date-time.'''

        try:
            datetime.fromisoformat(value)
            return True
        except TypeError:
            return True if isinstance(value, (date, datetime)) else False
        except ValueError:
            return False
        except AttributeError:
            return False

    @staticmethod
    def can_literal_eval(value):
        '''This function checks if the input value is a list, dict, tuple, set etc and returns True or False.
        @params value: Input value to check
        @return Boolean: True if value is a list, dict, tuple, set etc.'''

        try:
            literal_eval(value)
            return True
        except SyntaxError:
            return False
        except ValueError:
            return False
        except TypeError:
            return False
        except AttributeError:
            return False

    @staticmethod
    def is_complex(value):
        '''This function checks if the input value is a complex number or not and returns True or False.
        @params value: Input value to check
        @return Boolean: True if value is a complex number.'''

        if isinstance(value, str):
            value = value.replace(' ', '')
        try:
            complex(value)
            return True
        except ValueError:
            return False
        except TypeError:
            return False
        except AttributeError:
            return False

    @staticmethod
    def compare(value1, value2):
        '''Compares if two values are equal or not and returns True or False.
        @params value: Inputs 2 values to compare
        @return Boolean: True if the values are equal.'''

        return True if value1 == value2 else False

    @staticmethod
    def compare_date(value1, value2):
        '''Compares if dates of the two values are equal and returns True or False.
        @params value: Inputs dates as str(iso-datetime-format) or datetime parameter to be compared
        @return Boolean: True if the input values are equal'''

        if isinstance(value1, str):
            value1 = datetime.fromisoformat(value1)
        if isinstance(value2, str):
            value2 = datetime.fromisoformat(value2)
        value1 = str(value1.day) + '-' + str(value1.month) + '-' + str(value1.year)
        value2 = str(value2.day) + '-' + str(value2.month) + '-' + str(value2.year)
        return True if value1 == value2 else False

    @staticmethod
    def compare_datetime(value1, value2):
        '''Compares if dates and time of the two values are equal and returns True or False.
        @params value: Inputs 2 values to compare
        @return Boolean: True if the values are equal.'''

        if isinstance(value1, str):
            value1 = datetime.fromisoformat(value1)
        if isinstance(value2, str):
            value2 = datetime.fromisoformat(value2)
        value1 = str(value1.day) + '-' + str(value1.month) + '-' + str(value1.year) + ' ' + str(value1.hour) + ':' + str(value1.minute)
        value2 = str(value2.day) + '-' + str(value2.month) + '-' + str(value2.year) + ' ' + str(value2.hour) + ':' + str(value2.minute)
        return True if value1 == value2 else False

    @staticmethod
    def datatype_check(value):
        '''Checks if the value is float, complex, list, dict, tuple, set and returns the value in its correct datatype.
        @params value: Input value to check
        @return value: returns the input value in its correct datatype.'''

        if CompareVariables.is_float(value):
            return float(value)
        elif CompareVariables.is_complex(value):
            if isinstance(value, str):
                value = value.replace(' ', '')
            return complex(value)
        elif CompareVariables.can_literal_eval(value):
            return literal_eval(value)
        else:
            return value

    @staticmethod
    def compare_list_or_tuples_or_set(value1, value2):
        '''Checks if all the values inside a list, tuple, set are in their correct datatype and then compares the two values and returns True or False.
        @params value: Inputs 2 parameters to compare
        @return Boolean: True if the values are equal.'''

        if len(value1) == len(value2):
            for index, i in enumerate(value1):
                if CompareVariables.datatype_check(i) != CompareVariables.datatype_check(value2[index]):
                    return False
            return True
        else:
            return False

    @staticmethod
    def compare_dicts(value1, value2):
        '''Checks if all the values in the dict are in there correct datatype then compares the two input dicts and returns True or False.
        @params value: Inputs 2 dicts to compare
        @return Boolean: True if the values are equal.'''
        if len(value1) == len(value2):
            for i in value1:
                value1[CompareVariables.datatype_check(i)] = value1.pop(i)
            for i in value2:
                value2[CompareVariables.datatype_check(i)] = value2.pop(i)
            for i in value1:
                if CompareVariables.datatype_check(value1[i]) != CompareVariables.datatype_check(value2[i]):
                    return False
            return True
        else:
            return False

    @staticmethod
    def type_matching_and_compare(value1, value2):
        '''Compares two values and returns True or False irrespective of their datatype
        @params value: Inputs 2 parameters to compare
        @return Boolean: True if the values are equal.'''

        if CompareVariables.is_float(value1) and CompareVariables.is_float(value2):
            return CompareVariables.compare(float(value1), float(value2))
        elif CompareVariables.is_complex(value1) and CompareVariables.is_complex(value2):
            if isinstance(value1, str):
                value1 = value1.replace(' ', '')
            if isinstance(value2, str):
                value2 = value2.replace(' ', '')
            return CompareVariables.compare(complex(value1), complex(value2))
        elif bool(value1) == bool(value2) == False:
            return True
        elif CompareVariables.is_date_time(value1) and CompareVariables.is_date_time(value2):
            if type(value1) == date or type(value2) == date:
                return CompareVariables.compare_date(value1, value2)
            else:
                return CompareVariables.compare_datetime(value1, value2)
        elif CompareVariables.can_literal_eval(str(value1)) and CompareVariables.can_literal_eval(str(value2)):
            if type(literal_eval(str(value1))) == type(literal_eval(str(value2))):
                if isinstance(literal_eval(str(value1)), dict):
                    return CompareVariables.compare_dicts(literal_eval(str(value1)), literal_eval(str(value2)))
                elif isinstance(literal_eval(str(value1)), (list, tuple)):
                    return CompareVariables.compare_list_or_tuples_or_set(literal_eval(str(value1)), literal_eval(str(value2)))
                else:
                    return CompareVariables.compare(literal_eval(str(value1)), literal_eval(str(value2)))
            else:
                return False
        else:
            return CompareVariables.compare(str(value1).strip(), str(value2).strip())

