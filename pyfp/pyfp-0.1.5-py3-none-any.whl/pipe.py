from pyfp.helpers import min_arguments
from typing import TypeVar, Generic

T = TypeVar("T")

class Pipe(Generic[T]):
    """Allows you to structure your code in a pipe format."""

    def __init__(self, val: T) -> "Pipe":
        """Inits Pipe with it's initial value."""
        self._val = val

    @min_arguments(1)
    def to(self, *args) -> "Pipe":
        """Executes a new operation on the Pipe's value.
        
        Args:
            1st: 
                The operation to be performed. Must be either callable or a string containing the name of the method to be performed.
            2nd..nth:
                Arguments needed for the operation besides the value of the Pipe.

        Returns:
            The Pipe being operated on with an updated value.

        Raises:
            TypeError: Invalid argument: 1st argument must be either be a str or callable.
        """
        func = args[0]
        params = args[1:]

        if callable(func):
            self._val = func(*params, self._val)
        else:
            raise TypeError("Invalid argument: 1st argument must be either be a str or callable.")
        
        return self

    @min_arguments(1)
    def to_first(self, *args) -> "Pipe":
        """Executes a new operation on the Pipe's value in the first position.
        
        Args:
            1st: 
                The operation to be performed. Must be either callable or a string containing the name of the method to be performed.
            2nd..nth:
                Arguments needed for the operation besides the value of the Pipe.

        Returns:
            The Pipe being operated on with an updated value.

        Raises:
            TypeError: Invalid argument: 1st argument must be either be a str or callable.
        """
        func = args[0]
        params = args[1:]

        if callable(func):
            self._val = func(self._val, *params)
        else:
            raise TypeError("Invalid argument: 1st argument must be either be a str or callable.")
        
        return self

    def get(self) -> T:
        return self._val