import builtins

from functools import wraps

import json_settings as js


class Settings:
    """A base class for building python objects out of :obj:`dict` object.

    This class is designed as a recursive method of building python objects
    from json files.

    If the parsed json file does not match the defined settings class
    in attribute names and type, it will catch it an terminate with an error
    message.

    Example
    -------

    The following is a simple use case::

        class UserSettings(Settings):

            @Settings.assign
            def __init__(self, values: dict):
                self.setting_1 = int
                self.setting_2 = SubSetting

        class SubSetting(Settings):

            @Settings.assign
            def __init__(self, values: dict):
                self.subsetting_1 = str

    The `values` parameter should be, for example::

        values = {
            "setting_1": 1,
            "setting_2": {
                subsetting_1: "this_is_a_string"
            }
        }

    This results in::

        settings = UserSettings(values)

        print(settings.setting_1)
            # 1

        print(settings.setting_2.subsetting_1)
            # this_is_a_string

    """
    @staticmethod
    def assign(method):
        """A decorator that applies the
        :meth:`~.Settings.distribute` to parameter of the
        constructor of the derived class.

        """
        @wraps(method)
        def wrapper(self, *args):
            method(self, *args)
            self.distribute(*args)
            try:
                self.consistency_check()
            except AttributeError:
                pass
        return wrapper

    @property
    def primitive(self):
        """:obj:`list`(:obj:`type`) : a list of built in types.

        """
        return [getattr(builtins, d) for d in dir(builtins) if
                isinstance(getattr(builtins, d), type)]

    def distribute(self, values: dict):
        """The method which loops over the attribute/type pairs in the derived
        class' constructor and tries to find and assign values to them from the
        `values` parameter.

        Parameters
        ----------
        values : :obj:`dict`
            The dictionary that contains the values to be assigned to the
            derived class' attributes.

        Returns
        -------
        None

        Raises
        ------
        :class:`~.SettingNotFoundError`
            If one of the derived class' attributes cannot be found in
            `values`.

        :class:`~.js.SettingTypeError`
            If one of the type of one of the settings found in `values`
            is not of the required type, as defined in the derived class'
            constructor.
        
        :class:`~.SettingCheckError`
            If a check error is caught when assigning a setting to a
            :class:`~.Terminus` instance.

        Note
        ----
        If the setting found in the `values` is None, then this function will
        assign None as the setting value by default, independent of the expected
        value.

        """
        for setting, setting_type in self.__dict__.items():
            if not isinstance(values, dict):
                raise js.SettingTypeError(dict, type(values))
            try:
                try:
                    value = values[setting]
                except KeyError:
                    raise js.SettingNotFoundError()
            except js.SettingNotFoundError as e:
                raise js.SettingErrorMessage(setting, original_error=e)
            if value is None:
                setattr(self, setting, value)
            elif setting_type not in self.primitive:
                try:
                    setattr(self, setting, setting_type(value))
                except js.SettingTypeError as e:
                    raise js.SettingErrorMessage(setting, original_error=e)
                except js.SettingCheckError as e:
                    raise js.SettingErrorMessage(setting, original_error=e)
                except js.SettingNotFoundError as e:
                    raise js.SettingErrorMessage(setting, original_error=e)
                except js.SettingRangeTypeError as e:
                    raise js.SettingErrorMessage(setting, original_error=e)
                except js.SettingRangeKeyError as e:
                    raise js.SettingErrorMessage(setting, original_error=e)
                except js.SettingStringSelectionError as e:
                    raise js.SettingErrorMessage(setting, original_error=e)
                except js.ConsistencyError as e:
                    raise js.SettingErrorMessage(setting, original_error=e)
                except js.SettingErrorMessage as e:
                    raise js.SettingErrorMessage(setting, branch_error=e)
            else:
                try:
                    if isinstance(value, setting_type):
                        setattr(self, setting, value)
                    else:
                        raise js.SettingTypeError(setting_type, type(setting))
                except js.SettingTypeError as e:
                    raise js.SettingErrorMessage(setting, original_error=e)
        self.__source__ = values

    def __getattribute__(self, name):
        rv = object.__getattribute__(self, name)
        if issubclass(type(rv), js.TerminusSetting):
            return rv.get
        elif issubclass(type(rv), js.DictionarySetting):
            return rv.get
        elif issubclass(type(rv), js.ListSetting):
            return rv.get
        elif issubclass(type(rv), js.NumberSetting):
            return rv.get
        else:
            return rv

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def __hash__(self):
        return hash(str(self.__source__))
    
    def __eq__(self, other):
        if other.__hash__() == self.__hash__():
            return True
        else:
            return False
