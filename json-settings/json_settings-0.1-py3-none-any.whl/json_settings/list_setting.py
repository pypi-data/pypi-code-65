from collections.abc import Iterable

import json_settings as js


class ListSetting(js.Settings):

    """A base class for a list of settings classes.

    This class is used to store a number of settings objects. Instances must be
    of same type. 

    The implementation of the derived class constructor should be as follows::

        @Settings.assign
        def __init__(self, values: list):
            self.value = type
    
    Where `type` is the type of the objects that will be in the list.

    Attributes
    ----------
    type : :obj:`type`
        The attribute defined in the child class that determines the type of the
        setting stored in the class.

    value : :obj:`List`[:obj:`Any`]
        The list of value stored after all checks have been passed.

    """
    @property
    def get(self):
        return self.value

    def distribute(self, values: list):
        """Method called by the decorator :meth:`Settings.assign` that
        tries to assign the values passed to the constructor of the
        :class:`List` derived class.

        Parameters
        ----------
        values : :obj:`list`
            The values passed to the constructor of the :class:`List`
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

        if not isinstance(values, list):
            raise js.SettingTypeError(list, type(values))

        self.value = list()

        if self.type not in self.primitive:
            for idx, item in enumerate(values):
                try:
                    self.value.append(self.type(item))
                except js.SettingErrorMessage as e:
                    raise js.SettingErrorMessage(f"[{idx}]", e)
                except js.SettingTypeError as e:
                    raise js.SettingErrorMessage(f"[{idx}]", original_error=e)
                except js.SettingRangeTypeError as e:
                    raise js.SettingErrorMessage(f"[{idx}]", original_error=e)
                except js.SettingRangeKeyError as e:
                    raise js.SettingErrorMessage(f"[{idx}]", original_error=e)
                except js.ConsistencyError as e:
                    raise js.SettingErrorMessage(f"[{idx}]", original_error=e)
        else:
            for idx, item in enumerate(values):
                try:
                    if not isinstance(item, self.type):
                        raise js.SettingTypeError(self.type, type(item))
                    self.value.append(item)
                except js.SettingStringSelectionError as e:
                    raise js.SettingErrorMessage(f"[{idx}]", original_error=e)

    def __getitem__(self, key):
        """An overload of the list get item method.

        Returns the list or sub list or entry depending on `key`. If the items
        stored in the list are :class:`~.TerminusSetting` derived, then it will return
        a list or value which are the `value` attribute of the terminus
        instances.

        """
        rv = self.value[key]
        if issubclass(self.type, js.TerminusSetting):
            if isinstance(rv, Iterable):
                return [item.get for item in rv] 
            else:
                return rv.get
        else:
            return rv
    
    def __len__(self):
        """Mapping __len__ to attibute `value` __len__.
        
        Returns
        -------
        :obj:`int`
            The length of the stored list.

        """
        return len(self.value)

