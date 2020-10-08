from typing import TypeVar, Generic, Callable

T = TypeVar("T")
U = TypeVar("U")

class Option(Generic[T]):
    """A wrapper class for a value to represent the presence or absence of the value."""

    _val: T = None
    
    @staticmethod
    def some(val: T) -> "Option":
        """Init an instance of Option with the value given."""
        opt = Option()
        opt._val = val

        return opt

    @staticmethod
    def empty() -> "Option":
        """Init an instance of Option represnting the absence of a value."""
        return Option()

    def is_empty(self) -> bool:
        return True if self._val == None else False

    def is_some(self) -> bool:
        return True if self._val != None else False

    def unwrap(self) -> T:
        """Returns the stored value
        
        Raises:
            AssertError: Attempted to unwrap empty Option.
        """
        if self.is_empty():
            raise AssertionError("Attempted to unwrap empty Option.")

        return self._val

    def unwrap_or(self, default: T) -> T:
        """Returns the stored value if present otherwise returns the default value given.
        
        Args:
            default:
                The value to be returned if the Option is empty.

        Returns:
            The value contained in the option or the default value.
        """
        return self._val if self.is_some() else default

    def unwrap_or_else(self, default: Callable[[], T]) -> T:
        """Returns the stored value if present otherwise returns the computed value from default.

        Args:
            default:
                A callable object used to compute the default value.
        
        Returns:
            The value contained in the option or the default value.
        """
        return self._val if self.is_some() else default()

    def map(self, func: Callable[[T], U]) -> "Option":
        """Returns a new Option containing the value computed from calling func with the current Option's value.
        
        Args:
            func:
                A callable object used to compute the new Option's value.

        Returns:
            A new Option.
        """
        if self.is_some():
            return Option.some(func(self._val))
        
        return Option.empty()

    def map_or(self, default: T, func: Callable[[T], U]) -> "Option":
        """Returns a new Option containing the value computed from calling func with the current Option's value, or the default value given if the Option is empty.

        Args:
            default:
                The value of the new Option if the current option is empty.
            func:
                A callable object to compute the value of the new Option.

        Returns:
            A new Option.
        """
        if self.is_some():
            return Option.some(func(self._val))
        
        return Option.some(default)

    def map_or_else(self, default: Callable[[], U], func: Callable[[T], U]) -> "Option":
        """Returns a new Option containing the value computed from calling func with the current Option's value, or computed from the default value given if the Option is empty.
        
        Args:
            default:
                A callable object to compute the value of the new Option if the current option is empty.
        func:
                A callable object to compute the value of the new Option.
        
        Returns:
            A new Option.
        """
        if self.is_some():
            return Option.some(func(self._val))
        
        return Option.some(default())