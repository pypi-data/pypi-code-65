import json_settings as js


class DictionarySetting(js.Settings):
    """A base class for a dictionary of settings classes.

    This class is used to store a number of settings objects. Instances must be
    of same type. 

    The implementation of the derived class constructor should be as follows::

        @Settings.assign
        def __init__(self, values: dict):
            self.value = type
    
    Where `type` is the type of the objects that will be in the dictionary.

    Attributes
    ----------
    type : :obj:`type`
        The attribute defined in the child class that determines the type of the
        setting stored in the class.

    value : :obj:`Dict`[:obj:`str`, :obj:`Any`]
        The list of value stored after all checks have been passed.

    """

    @property
    def get(self):
        return self.value

    def distribute(self, values: dict):
        """Method called by the decorator :meth:`Settings.assign` that
        tries to assign the values passed to the constructor of the
        :class:`Dict` derived class.

        Parameters
        ----------
        values : :obj:`dict`
            The values passed to the constructor of the :class:`Dict`
            derived class.

        Returns
        -------
        None

        Raises
        ------
        :class:`~.TypeAttributeNotImplementedError`
            If the type attribute has not been defined in the derived class
            constructor. 

        :class:`~.TypeAttributeTypeError`
            If the :attr:`type` is not of type :obj:`type`

        :class:`~.SettingTypeError`
            If `values` is not a :obj:`list`.
        
        :class:`~.SettingsListTypeError`
            If any of the items in `values` are not of the required type,
            as specified in the derived class.

        :class:`~.SettingsErrorMessage`
            If any exceptions are raised when instantiating any subsettings.

        """
        if not hasattr(self, "type"):
            raise js.TypeAttributeNotImplementedError(self.__class__)
        if not isinstance(self.type, type):
            raise js.TypeAttributeTypeError(self.__class__)

        if not isinstance(values, dict):
            raise js.SettingTypeError(dict, type(values))

        self.value = dict()

        if self.type not in self.primitive:
            for key, value in values.items():
                try:
                    self.value[key] = self.type(value)
                except js.SettingErrorMessage as e:
                    raise js.SettingErrorMessage(key, e)
                except js.SettingRangeTypeError as e:
                    raise js.SettingErrorMessage(key, original_error=e)
                except js.SettingRangeKeyError as e:
                    raise js.SettingErrorMessage(key, original_error=e)
                except js.SettingStringSelectionError as e:
                    raise js.SettingErrorMessage(key, original_error=e)
                except js.ConsistencyError as e:
                    raise js.SettingErrorMessage(key, original_error=e)
        else:
            for key, value in values.items():
                try:
                    if not isinstance(value, self.type):
                        raise js.SettingTypeError(self.type, type(value))
                    self.value[key] = value
                except js.SettingTypeError as e:
                    raise js.SettingErrorMessage(key, original_error=e)
    
    def __getitem__(self, key):
        """An overload of the :obj:`dict` __getitem__ method.

        Returns the value for the given key. If the value is :class:`~.TerminusSetting`
        derived, then it will return `value` attribute of the terminus instance.

        """
        rv = self.value[key]
        if js.terminus_setting.TerminusSetting in rv.__class__.__bases__:
            return rv.value
        else:
            return rv
    
    def __len__(self):
        """Mapping __len__ to attribute `value` __len__.
        
        Returns
        -------
        :obj:`int`
            The length of the stored list.

        """
        return len(self.value)
    
    def keys(self):
        return self.value.keys()
    
    def values(self):
        if issubclass(self.type, js.terminus_setting.TerminusSetting):
            return {k: v.value for k, v in self.value.items()}.values()
        else:
            return self.value.values()
    
    def items(self):
        if issubclass(self.type, js.terminus_setting.TerminusSetting):
            return {k: v.value for k, v in self.value.items()}.items()
        else:
            return self.value.items()

