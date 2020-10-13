from typing import Union

import json_settings as js


class Error(Exception):
    """The base class fro mwhich all other Error classes inherit

    """
    pass


class SettingRangeKeyError(Error):
    """The exception raised when a :class:`~.Number` instance is missing an 
    entry in a range specification.

    """
    def __init__(self, key: str):
        """The constructor for the :class:`SettingRangeKeyError` class.

        """
        self.msg = f"No '{key}' parameter provided for range"


class SettingRangeTypeError(Error):
    """The exception raised when a :class:`~.Number` instance is passed an
    incorrect type in a range specification. 

    """
    def __init__(self, key: str, expected_type):
        """The constructor for the :class:`SettingRangeTypeError` class.

        """
        self.msg = f"The '{key}' parameter was not {expected_type}"


class SettingStringSelectionError(Error):
    """The exception raised when a :class:`~.StringSelection` instance is
    passed an invalid value.

    """
    def __init__(self, allowed: js.StringList):
        """The constructor for the :class:`SettingRangeTypeError` class.

        """
        self.msg = f"must be one of {allowed}"


class SettingNotFoundError(Error):
    """The exception raised when a setting cannot be found in the passed
    :obj:`dict`.

    """
    def __init__(self):
        """The constructor for the :class:`SettingNotFoundError` class.

        """
        self.msg = "Setting not found." 


class SettingCheckError(Error):
    """The exception raised when a :class:`Terminus` fails its value check.

    """
    def __init__(self, raised_exception, value):
        """The constructor for the :class:`SettingCheckError` class.

        Parameters
        ----------
        raised_exception 
            The exception raised by the test.
        value : T
            The value which failed the check.
        """
        self.raised_exception = raised_exception
        self.msg = raised_exception
        

class SettingTypeError(Error):
    """The exception raised when the setting found in the passed :obj:`dict`
    is of the wrong type, when instantiating a :class:`~.Dict` object.

    """
    def __init__(self, expected: type, actual: type):
        """The constructor for the :class::`SettingDictTypeError` class.

        Parameters
        ----------
        expected : :obj:`type`
            The expected type.
        
        actual : :obj:`type`
            The received type.

        """
        self.msg = f"Expecting : {expected} | Received: {actual}"


class SettingErrorMessage(Error):
    """The exception raised when the setting found in the passed :obj:`dict`
    is of the wrong type.

    """
    def __init__(self,
                 current_name: str,
                 branch_error = None,
                 original_error: Union[SettingCheckError, SettingTypeError] = None):
        """The constructor for the :class::`SettingTypeError` class.

        Parameters
        ----------
        setting : :obj:`str`
            The name of the setting which has an incorrect type passed.

        setting_type : :obj:`type`
            The expected type of the setting.
        """
        if original_error:
            self.route = [current_name]
            self.original_error = original_error

        elif branch_error:
            self.route = [current_name] + branch_error.route
            self.original_error = branch_error.original_error
        else:
            raise ValueError("Must pass either new error or branch error as parameter.")

        super().__init__(self.build_message())
    
    def build_message(self):
        rv = str()
        join = " -> "
        for item in self.route:
            if "[" in item: 
                rv = rv[:-len(join)]
            rv += f"{item}" + join
        rv += f"{str(self.original_error.msg)}"
        return rv


class OptionsAttributeNotImplementedError(Error):
    """The exception raised when the `options` attribute has not been defined
    in a StringSelection derived class.

    """
    def __init__(self, derived_class):
        """The constructor for the :class::`OptionsAttributeNotImplementedError`
        class.

        Parameters
        ----------
        derived_class : :obj:`type`
            The name of the derived class that raised the exception.
        
        """
        self.msg = f"The {derived_class} class does not have a self.options"\
                   f"attribute defined in its constructor."
  

class OptionsAttributeTypeError(Error):
    """The exception raised when the value of the `options` attribute defined
    in a StringSelection derived class is not a :obj:`list`, or one of its
    elements is not a string.

    """
    def __init__(self, derived_class):
        """The constructor for the :class::`OptionsAttributeTypeError`
        class.

        Parameters
        ----------
        derived_class : :obj:`type`
            The name of the derived class that raised the exception.
        
        """
        self.msg = f"The {derived_class} class self.options attribute's value "\
                   f"is not of type {list}, or one of its elements is not of"\
                   f" type {str}"
        super().__init__(self.msg)
        

class TypeAttributeNotImplementedError(Error):
    """The exception raised when the `type` attribute has not been defined
    in a Terminus, Number, List, or Dict derived class.

    """
    def __init__(self, derived_class):
        """The constructor for the :class::`TypeAttributeNotImplementedError`
        class.

        Parameters
        ----------
        derived_class : :obj:`type`
            The name of the derived class that raised the exception.
        
        """
        self.msg = f"The {derived_class} class does not have a self.type "\
                   f"attribute defined in its constructor."
        super().__init__(self.msg)
 

class TypeAttributeTypeError(Error):
    """The exception raised when the value of the `type` attribute defined
    in a Terminus, Number, List, or Dict derived class is not a :obj:`type`.

    """
    def __init__(self, derived_class):
        """The constructor for the :class::`TypeAttributeTypeError`
        class.

        Parameters
        ----------
        derived_class : :obj:`type`
            The name of the derived class that raised the exception.
        
        """
        self.msg = f"The {derived_class} class self.type attribute's value is"\
                   f" not of type `type`."
        super().__init__(self.msg)


class ConsistencyError(Error):
    """The exception raised if a consistency check is failed.

    """

    def __init__(self, msg: str):
        """The constructor for the :class:`ConsistencyError` class

        Parameters
        ----------

        """
        self.msg = msg
        super().__init__(msg)
