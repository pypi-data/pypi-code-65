from typing import Callable, Any


class MyOperatorException(Exception):
    """MyOperatorException."""

    def __init__(self, message: str) -> None:
        """__init__.

        :param message:
        :type message: str
        :rtype: None
        """
        self._message: str = self.set_message(message)

    def set_message(self, message: str) -> str:
        """set_message.

        :param message:
        :type message: str
        :rtype: str
        """
        return message

    def get_message(self) -> str:
        """get_message.

        :rtype: str
        """
        return self._message

    def __str__(self) -> str:
        """__str__.

        :rtype: str
        """
        return self.get_message()


def factory_operator(Left: type, Right: type, Output: type) -> type:
    """factory_operator.

    :param Left:
    :type Left: type
    :param Right:
    :type Right: type
    :param Output:
    :type Output: type
    :rtype: type
    """

    class MyOperator:
        """MyOperator."""

        def __init__(
            self,
            function: Callable[[Any, Any], Any],
            left: Any = None,
            right: Any = None,
        ) -> None:
            """__init__.

            :param function:
            :type function: Callable[[Any, Any], Any]
            :param left:
            :type left: Any
            :param right:
            :type right: Any
            :rtype: None
            """
            self.function: Callable[[Any, Any], Any] = function
            self.left: Any = left
            self.right: Any = right

        def __rmul__(self, left: Any) -> Any:
            """__rmul__.

            :param left:
            :type left: Any
            :rtype: Any
            """
            if type(left) != Left:
                raise MyOperatorException(
                    "A argument has type {} but expected {}".format(
                        type(left).__name__, Left.__name__
                    )
                )
            if self.right is None:
                if self.left is None:
                    return MyOperator(self.function, left=left)
                else:
                    raise MyOperatorException("Missing left argument")
            else:
                output = self.function(left, self.right)
                if type(output) != Output:
                    raise MyOperatorException(
                        "A output has type {} but expected {}".format(
                            type(output).__name__, Output.__name__
                        )
                    )

                return output

        def __mul__(self, right: Any) -> Any:
            """__mul__.

            :param right:
            :type right: Any
            :rtype: Any
            """
            if type(right) != Right:
                raise MyOperatorException(
                    "A argument has type {} but expected {}".format(
                        type(right).__name__, Right.__name__
                    )
                )

            if self.left is None:
                if self.right is None:
                    return MyOperator(self.function, right=right)
                else:
                    raise MyOperatorException("Missing right argument")
            else:
                output = self.function(self.left, right)
                if type(output) != Output:
                    raise MyOperatorException(
                        "A output has type {} but expected {}".format(
                            type(output).__name__, Output.__name__
                        )
                    )

                return output

    return MyOperator
