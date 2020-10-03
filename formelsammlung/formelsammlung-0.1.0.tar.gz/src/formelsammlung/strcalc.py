# noqa: D205,D208,D400
"""
    formelsammlung.strcalc
    ~~~~~~~~~~~~~~~~~~~~~~

    Calculate arithmetic expressions from strings.

    :copyright: (c) Christian Riedel
    :license: GPLv3
"""
import ast
import operator

from typing import Optional, Union


NumberType = Union[int, float, complex]


class _StringCalculator(ast.NodeVisitor):
    """Calculate an arithmetic expression from a string using :mod:`ast`."""

    # pylint: disable=C0103,R0201
    def visit_BinOp(self, node: ast.BinOp) -> NumberType:  # noqa: N802
        """Handle `BinOp` nodes."""
        return {
            ast.Add: operator.add,  #: a + b
            ast.Sub: operator.sub,  #: a - b
            ast.Mult: operator.mul,  #: a * b
            ast.Pow: operator.pow,  #: a ** b
            ast.Div: operator.truediv,  #: a / b
            ast.FloorDiv: operator.floordiv,  #: a // b
            ast.Mod: operator.mod,  #: a % b
        }[type(node.op)](self.visit(node.left), self.visit(node.right))

    # fmt: off
    def visit_UnaryOp(self, node: ast.UnaryOp) -> NumberType:  # noqa: N802
        """Handle `UnaryOp` nodes."""
        return {
            ast.UAdd: operator.pos,  #: + a
            ast.USub: operator.neg,  #: - a
        }[type(node.op)](self.visit(node.operand))
    # fmt: on

    def visit_Constant(self, node: ast.Constant) -> NumberType:  # noqa: N802
        """Handle `Constant` nodes."""
        return node.value

    def visit_Num(self, node: ast.Num) -> NumberType:  # noqa: N802
        """Handle `Num` nodes.

        For backwards compatibility <3.8. Since 3.8 ``visit_Constant`` is used.
        """
        return node.n

    def visit_Expr(self, node: ast.Expr) -> NumberType:  # noqa: N802
        """Handle `Expr` nodes."""
        return self.visit(node.value)


def calculate_string(expression: str) -> Optional[NumberType]:
    """Calculate the given expression.

    The given arithmetic expression string is parsed as an :mod:`ast` and then
    handled by the :class:`ast.NodeVisitor`.

    Python exceptions are risen like with normal arithmetic expression e.g.
    :class:`ZeroDivisionError`.

    Supported number types:

        - :class:`int` ``1``
        - :class:`float` ``1.1``
        - :class:`complex` ``1+1j``

    Supported mathematical operators:

        - Positive (:func:`operator.pos`) ``+ a``
        - Negative (:func:`operator.neg`) ``- a``
        - Addition (:func:`operator.add`) ``a + b``
        - Subtraction (:func:`operator.sub`) ``a - b``
        - Multiplication (:func:`operator.mul`) ``a * b``
        - Exponentiation (:func:`operator.pow`) ``a ** b``
        - Division (:func:`operator.truediv`) ``a / b``
        - FloorDivision (:func:`operator.floordiv`) ``a // b``
        - Modulo (:func:`operator.mod`) ``a % b``

    :param expression: String with arithmetic expression.
    :return: Result or None
    """
    if expression == "":
        return None
    return _StringCalculator().visit(ast.parse(expression).body[0])
