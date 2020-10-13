from numpy import linspace

import json_settings as js


class NumberSetting(js.TerminusSetting):
    """The special Terminus variant that is for numerical values.

    This class support range values in the form of arrays of min/max/num
    definitions.

    Attributes
    ----------
    value : :obj:`Union`[:obj:`float`, :obj:`int`, :obj:`List`]
        The value or list of values stored.
    
    """

    @property
    def is_range(self):
        """:obj:`bool` : True if the instance contains a range of values.
        
        """
        return self._range
    
    @property
    def match(self):
        """:obj:`Union`[None, :obj:`str`] : The match parameter.

        """
        return self._match

    def distribute(self, value):
        """Method called by the decorator :meth:`Terminus.assign` that
        tries to assign the values passed to the constructor of the
        :class:`Number` derived class.

        Parameters
        ----------
        value : :obj:`Union`[:obj:`float`, :obj:`int`, :obj:`dict`]
            
        Raises
        ------
        :class:`~.TypeAttributeNotImplementedError`
            If the type attribute has not been defined in the derived class
            constructor. 

        :class:`~.TypeAttributeTypeError`
            If the :attr:`type` is not of type :obj:`type`

        :class:`~.SettingTypeError`
            If `values` is not a number or valid range dictionary.
        
        """
        if not hasattr(self, "type"):
            raise js.TypeAttributeNotImplementedError(self.__class__)
        if not isinstance(self.type, type):
            raise js.TypeAttributeTypeError(self.__class__)

        if type(value) is self.type:
            self.__value(value)
        elif type(value) is dict and "array" in value:
            self.__array(value)
        elif type(value) is dict:
            self.__range(value)
        else:
            raise js.SettingTypeError(
                f"{self.type} || {{'array': [{self.type}]}} || "
                f"{{'min': {self.type}, 'max': {self.type}, 'num': {int}}}",
                type(value))
    
    def __value(self, value):
        """The method that assigns the attributes if a single value is passed.

        Parameters
        ----------
        value : :obj:`Union`[:obj:`float`, :obj:`int`]
            The value to be stored.

        """
        self.value = value
        self._range = False
        self._match = None
    
    def __array(self, value: dict):
        """The method that assigns the attributes if a array of value is passed.

        Parameters
        ----------
        value : :obj:`dict`[:obj:`str`, :obj:`list`]
            The dictionary with "array": listofvalues.

        Raises
        ------
        :class:`~.SettingTypeError`
            If the values in the array are not the same type as :attr:`type`

        """
        for item in value["array"]:
            if not isinstance(item, self.type):
                raise js.SettingTypeError(self.type, type(item))
        self.value = value["array"]
        self._range = True
        try:
            self._match = value["match"]
        except KeyError:
            self._match = None

    def __range(self, value: dict):
        """The method that assigns the attributes if a array of value is passed.

        Parameters
        ----------
        value : :obj:`dict`
            The dictionary with the range definition. Must be of the form::

                {
                    "max": value,
                    "min": value,
                    "num": int
                }
            
            Where value is of the defined type.

        Raises
        ------
        :class:`~.SettingRangeTypeError`
            If type(`value`["min"]) is not :attr`type`.

        :class:`~.SettingRangeKeyError`
            If `value`["min"] does not exist.

        :class:`~.SettingRangeTypeError`
            If type(`value`["max"]) is not :attr`type`.

        :class:`~.SettingRangeKeyError`
            If `value`["max"] does not exist.

        :class:`~.SettingRangeTypeError`
            If type(`value`["num"]) is not :obj:`int`. 

        :class:`~.SettingRangeKeyError`
            If `value`["num"] does not exist.

        """
        try:
            if not isinstance(value["min"], self.type):
                raise js.SettingRangeTypeError("min", self.type)
        except KeyError:
            raise js.SettingRangeKeyError("min")
        try:
            if not isinstance(value["max"], self.type):
                raise js.SettingRangeTypeError("max", self.type)
        except KeyError:
            raise js.SettingRangeKeyError("max")
        try:
            if not isinstance(value["num"], int):
                raise js.SettingRangeTypeError('num', int)
        except KeyError:
            raise js.SettingRangeKeyError("num")
        self.value = linspace(value['min'], value['max'], abs(value['num']))
        self.value = [self.type(item) for item in self.value]
        self._range = True
        try:
            self._match = value["match"]
        except KeyError:
            self._match = None

    def lower_bound(self, value):
        """Checks if values are above or equal to a lower bound.
        
        Helper function to be called in derived class check implementation.

        Parameters
        ----------
        value : :obj:`Union`[:obj:`float`, :obj:`int`]
            The lower bound.

        Raises
        ------
        :obj:`ValueError`
            If any values are less than or equal to the provided bound.

        """
        if isinstance(self.value, self.type):
            if self.value < value:
                raise ValueError(f"must be >= {value}")
        elif isinstance(self.value, list):
            for item in self.value:
                if item < value:
                    raise ValueError(f"must be >= {value}")
        elif isinstance(self.value, dict):
            if self.value["min"] < value:
                raise ValueError(f"must be >= {value}")
            if self.value["max"] < value:
                raise ValueError(f"must be >= {value}")
    
    def upper_bound(self, value):
        """Checks if values are below or equal to an upper bound.
        
        Helper function to be called in derived class check implementation.

        Parameters
        ----------
        value : :obj:`Union`[:obj:`float`, :obj:`int`]
            The upper bound.

        Raises
        ------
        :obj:`ValueError`
            If any values are greater than or equal to the provided bound.

        """
        if isinstance(self.value, self.type):
            if self.value > value:
                raise ValueError(f"must be <= {value}")
        elif isinstance(self.value, list):
            for item in self.value:
                if item > value:
                    raise ValueError(f"must be <= {value}")
        elif isinstance(self.value, dict):
            if self.value["min"] > value:
                raise ValueError(f"must be <= {value}")
            if self.value["max"] > value:
                raise ValueError(f"must be <= {value}")
    
    def lower_bound_exclusive(self, value):
        """Checks if values are above an upper bound.
        
        Helper function to be called in derived class check implementation.

        Parameters
        ----------
        value : :obj:`Union`[:obj:`float`, :obj:`int`]
            The lower bound.

        Raises
        ------
        :obj:`ValueError`
            If any values are greater than the provided bound.

        """
        if isinstance(self.value, self.type):
            if self.value <= value:
                raise ValueError(f"must be > {value}")
        elif isinstance(self.value, list):
            for item in self.value:
                if item <= value:
                    raise ValueError(f"must be > {value}")
        elif isinstance(self.value, dict):
            if self.value["min"] <= value:
                raise ValueError(f"must be > {value}")
            if self.value["max"] <= value:
                raise ValueError(f"must be > {value}")
    
    def upper_bound_exclusive(self, value):
        """Checks if values are above an lower bound.
        
        Helper function to be called in derived class check implementation.

        Parameters
        ----------
        value : :obj:`Union`[:obj:`float`, :obj:`int`]
            The lower bound.

        Raises
        ------
        :obj:`ValueError`
            If any values are greater than the provided bound.

        """
        if isinstance(self.value, self.type):
            if self.value >= value:
                raise ValueError(f"must be < {value}")
        elif isinstance(self.value, list):
            for item in self.value:
                if item >= value:
                    raise ValueError(f"must be < {value}")
        elif isinstance(self.value, dict):
            if self.value["min"] >= value:
                raise ValueError(f"must be < {value}")
            if self.value["max"] >= value:
                raise ValueError(f"must be < {value}")
 