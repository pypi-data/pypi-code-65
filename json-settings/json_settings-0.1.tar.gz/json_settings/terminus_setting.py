from abc import ABC
from abc import abstractmethod

from functools import wraps

import json_settings as js


class TerminusSetting(ABC):
    """A base class for a terminating setting.

    This class is used to store a single setting in a :class:`~.Settings`
    derived class.

    If the expected type of a :class:`~.Settings` derived class attribute
    inherits from :class:`Termninus`, then when __getattribute__ is called to
    access the :class:`Terminus` instance, it will return the :attr:`value`
    attribute instead.

    This structure allows for value checks to be applied to individual settings,
    on instantiation of :class:`~.Settings` derived classes.

    As with the :class:`~.Settings` derived classes, the decorator
    :meth:`Terminus.assign` should be applied to :class:`Terminus` derived class
    constructors. If this is done, the abstract method :meth:`Terminus.check` is
    automatically called after the derived class' constructor.

    Attributes
    ----------
    type : :obj:`type`
        The attribute defined in the child class that determines the type of the
        setting stored in the class.

    value : :obj:`Any`
        The value stored after all checks have been passed.

    """
    @property
    def get(self):
        return self.value

    @staticmethod
    def assign(method):
        """A decorator that applies the :meth:`Terminus.distribute` to
        parameter of the constructor of the derived class. It will also then
        call the :meth:`Terminus.check` function.

        """
        @wraps(method)
        def wrapper(self, *args):
            method(self, *args)
            self.distribute(*args)
            self.action()
        return wrapper

    @abstractmethod
    def check(self):
        """An abstract method that defines the value checks to be performed on
        the settings stored in this class.

        Raises
        ------
        :class:`~.TypeError`
            If the passed value is of the wrong type.
        
        :obj:`ValueError`
            If the passed value is outside acceptable bounds.

        """
        pass

    def action(self):
        """Method that handles exceptions thrown by the :meth:`Terminus.check`
        function.

        Parameters
        ----------
        check_method
            The abstract check method implementation to be called.

        Raises
        ------
        :class:`~.SettingCheckError`
            If the check function raises any exceptions.

        """
        try:
            self.check()
        except TypeError as e:
            raise js.SettingCheckError(e, self.value)
        except ValueError as e:
            raise js.SettingCheckError(e, self.value)

    def distribute(self, value):
        """Method called by the decorator :meth:`Terminus.assign` that
        tries to assign the value passed to the constructor of the
        :class:`Terminus` derived class.

        Parameters
        ----------
        value : :class:`TypeVar`
            The value passed to the constructor of the :class:`Terminus`
            derived class.

        Raises
        ------
        :class:`~.TypeAttributeNotImplementedError`
            If the type attribute has not been defined in the derived class
            constructor. 

        :class:`~.TypeAttributeTypeError`
            If the :attr:`type` is not of type :obj:`type`

        :class:`~.SettingTypeError`
            If the type of the passed value is not :attr:`type`.

        """
        if not hasattr(self, "type"):
            raise js.TypeAttributeNotImplementedError(self.__class__)
        if not isinstance(self.type, type):
            raise js.TypeAttributeTypeError(self.__class__)
        if not isinstance(value, self.type):
            raise js.SettingTypeError(self.type, type(value))
        self.value = value

