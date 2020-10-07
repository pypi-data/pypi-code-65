"""Tree data structure."""

from typing import Dict, Iterator, List, MutableMapping, Tuple, TypeVar

import attr

Key = TypeVar("Key")
Value = TypeVar("Value")


@attr.s(auto_attribs=True)
class Tree(MutableMapping[Tuple[Key, ...], Value]):
    """
    Tree data structure.

    Values at nodes are optional. Children are named and ordered.
    """

    value: List[Value] = attr.ib(factory=list, init=False)
    children: Dict[Key, "Tree[Key, Value]"] = attr.ib(factory=dict, init=False)

    def __iter__(self) -> Iterator[Tuple[Key, ...]]:
        """Iterate over the tree keys."""
        if self.value:
            yield ()
        for key, child in self.children.items():
            yield from ((key,) + k for k in child)

    def __len__(self) -> int:
        """Count the number of nodes with values."""
        return sum((len(child) for child in self.children.values()), len(self.value))

    def __getitem__(self, key: Tuple[Key, ...]) -> Value:
        """Retrieve a value from the tree by key."""
        if key:
            try:
                return self.children[key[0]][key[1:]]
            except KeyError as e:
                raise KeyError((key[0],) + e.args) from None
        if self.value:
            return self.value[0]
        raise KeyError(())

    def __setitem__(self, key: Tuple[Key, ...], value: Value) -> None:
        """Set a value by key."""
        if key:
            if key[0] not in self.children:
                self.children[key[0]] = Tree()
            self.children[key[0]][key[1:]] = value
        else:
            self.value = [value]

    def __delitem__(self, key: Tuple[Key, ...]) -> None:
        """Remove a value by key."""
        # Attempt to access the value; this will throw if it is not present.
        self[key]  # pylint: disable=pointless-statement
        if key:
            del self.children[key[0]][key[1:]]
            if not self.children[key[0]]:
                del self.children[key[0]]
        else:
            self.value = []

    def __str__(self) -> str:
        """Pretty-print a string representation of the tree."""
        return self._str(".")

    def _str(self, root: str) -> str:
        """Pretty-print the tree using the supplied name for this node."""
        if self.value:
            root += f":{_breaklines(str(self.value[0]))}"
        elements = [root]
        for i, (key, child) in enumerate(self.children.items()):
            if i == len(self.children) - 1:
                # pylint: disable=protected-access
                elements.append(_indent(child._str(str(key)), "└─ ", "   "))
            else:
                elements.append(
                    _indent(
                        child._str(str(key)),  # pylint: disable=protected-access
                        "├─ ",
                        "│  ",
                    )
                )
        return "\n".join(elements)


def _indent(s: str, head_prefix: str, tail_prefix: str) -> str:
    return "\n".join(
        (tail_prefix if lineno else head_prefix) + line
        for lineno, line in enumerate(s.splitlines())
    )


def _breaklines(s: str) -> str:
    lines = s.splitlines()
    if len(lines) <= 1:
        return " " + s
    return f"\n{_indent(s, '  ', '  ')}"
