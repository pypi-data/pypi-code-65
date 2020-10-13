import json_settings as js

class StringSetSetting(js.TerminusSetting):
    """The as class that stores a string from a predefined list.

    Attributes
    ----------
    type : :obj:`type`
        The attribute defined in the child class that determines the type of the
        setting stored in the class.

    value: :obj:`str`
        The stored string.
    
    options : :obj:`List`[:obj:`str`]
        The predefined list of string that are valid. This attribute should be
        defined in the child constructor.

    """
    
    @property
    def get(self):
        return self.value

    def distribute(self, value: str):
        """Method called by the decorator :meth:`Settings.assign` that
        tries to assign the values passed to the constructor of the
        :class:`Dict` derived class.

        Parameters
        ----------
        value: :obj:`str`
            The value to be stored.

        Raises
        ------
        :class:`~.OptionsAttributeNotImplementedError`
            If the :attr:`options` attribute has not been defined in the derived
            class constructor.

        :class:`~.OptionsAttributeTypeError`
            If the item contained in the :attr:`options` attribute are not
            strings.

        :class:`~.SettingTypeError`
            If the passed value `value` is not a :obj:`str`.

        :class:`~.SettingStringSelectionError`
            If the passed value `value` is not in :attr:`options`.

        """
        if not hasattr(self, "options"):
            raise js.OptionsAttributeNotImplementedError(self.__class__)
        if not isinstance(self.options, list):
            raise js.OptionsAttributeTypeError(self.__class__)
        if not isinstance(value, str):
            raise js.SettingTypeError(str, type(value))
        elif value not in self.options:
            raise js.SettingStringSelectionError(self.options)
        else:
            self.value = value

    def check(self):
        pass
