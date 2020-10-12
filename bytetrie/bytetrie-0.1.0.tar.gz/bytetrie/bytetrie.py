from __future__ import annotations
from typing import Sequence, MutableSequence, ByteString, Any, Optional
from abc import ABC, abstractmethod
from .util import (has_common_prefix, common_prefix, is_prefix_of, find_first,
                   cut_off_prefix)

import logging
log = logging.getLogger(__name__)

class ByteTrie:
    def __init__(self, multi_value:bool=False):
        self.root = Root([])
        self.multi_value = multi_value

    def insert(self, label: ByteString, content: Any):
        log.info(f"Inserting {label} into Trie")
        start = self.root.child_by_common_prefix(label)
        if not start:
            log.debug(f"Creating new terminal for {label} at root")
            new_node = Terminal(label, content, self.root, [], self.multi_value)
            self.root.put_child(new_node)
            return new_node
        log.debug(f"Found match {start} for {label}. Traversing down")
        self._insert(start, label, content)

    def _insert(self, node, label, content):
        log.info(f"Inserting {label} into Trie at {node}")
        if node.has_label(label):
            log.debug(f"{node} equals {label}. Wrapping node as Terminal.")
            if isinstance(node, Terminal) and not self.multi_value:
                log.warning(f"{node} is already a Terminal. Content will be overwritten.")
            terminal = Terminal.from_child(node, content, self.multi_value)
            node.replace_with(terminal)
            return terminal

        if node.is_prefix_of(label):
            log.debug(f"{node} is prefix of {label}")
            cutoff = node.cut_from(label)
            next_node = node.child_by_common_prefix(cutoff)
            if not next_node:
                log.debug(f"No matching child found for {cutoff}. Creating new child terminal.")
                terminal = Terminal(cutoff, content, node, [], self.multi_value)
                node.put_child(terminal)
                return terminal
            else:
                log.debug(f"Found match {next_node} for {cutoff}. Traversing down.")
                return self._insert(next_node, cutoff, content)

        if node.starts_with(label):
            log.debug(f"{label} is part of {node}. Creating new parent from {label}")
            new_node = Terminal(label, content, node.parent, [], self.multi_value)
            node.replace_with(new_node)
            node.strip_prefix(label)
            new_node.put_child(node)
            return new_node

        log.debug(f"{label} and {node} have a common ancestor")
        common_prefix = node.common_prefix(label)
        log.debug(f"Creating new ancestor for {common_prefix}")
        ancestor = Child(common_prefix, node.parent, [])
        node.replace_with(ancestor)
        terminal = Terminal(cut_off_prefix(common_prefix, label), content, ancestor, [], self.multi_value)
        node.strip_prefix(common_prefix)
        ancestor.put_child(terminal)
        ancestor.put_child(node)
        return terminal

    def find(self, prefix: ByteString) -> Sequence[Terminal]:
        node = self._find(self.root, prefix)
        return self._get_terminals(node)

    def _find(self, node, prefix, collector=""):
        cutoff = node.cut_from(prefix)
        log.debug(f"Searching for {cutoff} in {node}")
        child = node.child_by_prefix_match(cutoff)
        if not child and not cutoff:
            return node
        elif not child and cutoff:
            log.debug(f"Leftover cutoff {cutoff}. Trying to find node with prefix {cutoff}")
            child = node.child_by_common_prefix(cutoff)
            if not child or not child.starts_with(cutoff):
                return None
            log.debug(f"Found child {child} starting with {cutoff}")
            return child
        else: # child must be not None
            log.debug(f"Found node {child} in {node} for {cutoff}. Traversing down.")
            return self._find(child, cutoff)

    def _get_terminals(self, node):
        if not node: return []

        collector = []
        if isinstance(node, Terminal):
            collector.append((node))
        for child in node.children:
            collector.extend(self._get_terminals(child))
        return collector

    def to_dot(self) -> str:
        return "graph {\n\n"+self.root.to_dot()+"\n}"


class Node(ABC):
    def __init__(self, children: MutableSequence[Child]):
        self.children = children

    def child_by_common_prefix(self, label: ByteString) -> Optional[Child]:
        """ Return Child that has a common prefix with label if one exists. """
        def by_common_prefix(child: Child):
            return has_common_prefix(child.label, label)
        return find_first(by_common_prefix, self.children)

    def child_by_prefix_match(self, label: ByteString) -> Optional[Child]:
        """ Return Child which label is a prefix of the given label if one exists. """
        def by_prefix_match(child: Child):
            return is_prefix_of(child.label, label)
        return find_first(by_prefix_match, self.children)

    def put_child(self, child: Child):
        """ Put child into this node's children. Replacing existing children. """
        if child in self.children:
            log.warning(f"Replacing child {child.label}")
            self.remove_child(child)
        child.parent = self
        self.children.append(child)

    def replace_child(self, child: Child, replacement: Child):
        """ Remove child from this node's children and add replacement. """
        self.remove_child(child)
        self.put_child(replacement)

    def remove_child(self, child: Child):
        """ Remove child from this node's children """
        if not child in self.children:
            log.warning(f"Trying to delete {child.label} but it does not exist.")
        self.children.remove(child)

    @abstractmethod
    def dot_label(self) -> str:
        """ Readable label for this node in a dot graph """
        ...

    @abstractmethod
    def dot_id(self) -> str:
        """ Technical id for this node in a dot graph. Must be unique. """
        ...

    @abstractmethod
    def cut_from(self, label: ByteString) -> ByteString:
        """ Cut off node's label considered as prefix from label. """
        ...

    def to_dot(self) -> str:
        s = f'{self.dot_id()} [label="{self.dot_label()}"]\n'
        for child in self.children:
            s += f"{self.dot_id()} -- {child.dot_id()}\n"
            s += child.to_dot()
        return s

class Root(Node):
    def cut_from(self, label: ByteString) -> ByteString:
        return label

    def dot_label(self):
        return "root"

    def dot_id(self):
        return "root"

class Child(Node):
    def __init__(self, label: ByteString, parent: Node, children: MutableSequence[Child]):
        self.label = label
        self.parent = parent
        self.children = children

    def __eq__(self, other_child):
        return (isinstance(other_child, Child)
                and self.label == other_child.label)

    def __hash__(self):
        return hash(self.label)

    def __str__(self):
        return self.label.decode('utf-8', 'replace').replace('"', '\\"')

    def dot_label(self):
        return self.label.decode('utf-8', 'replace').replace('"', '\\"')

    def dot_id(self):
        return id(self)

    def has_label(self, label):
        return self.label == label

    def is_prefix_of(self, label):
        return is_prefix_of(self.label, label)

    def replace_with(self, new_child: Child):
        new_child.parent = self.parent
        self.parent.replace_child(self, new_child)

    def starts_with(self, label: ByteString) -> bool:
        return is_prefix_of(label, self.label)

    def cut_from(self, label: ByteString) -> ByteString:
        """ Cut node's label from (start of) label """
        return cut_off_prefix(self.label, label)

    def strip_prefix(self, prefix: ByteString):
        """ Cut off prefix from node's label """
        self.label = cut_off_prefix(prefix, self.label)

    def extend(self, label: ByteString) -> ByteString:
        """ Extend label by node's label """
        return bytes(label) + bytes(self.label)

    def split_label_at(self, index):
        return (self.label[:index], self.label[index:])

    def contains(self, label):
        if len(label) > len(self.label):
            return False
        for (a,b) in zip(self.label, label):
            if a != b: return False
        return True

    def common_prefix(self, label):
        return common_prefix(self.label, label)

class Terminal(Child):
    def __init__(self, label: ByteString, content: Any, parent: Node, children: MutableSequence[Child], multi_value: bool):
        super().__init__(label, parent, children)
        self.multi_value = multi_value
        self.content = [content] if multi_value else content

    @classmethod
    def from_child(cls, child: Child, content: Any, multi_value: bool):
        # multi_value param has no effect if already a Terminal. I.e.
        # from_child cannot change the multi-value stage of a child that
        # is already a Terminal
        if isinstance(child, Terminal) and child.multi_value:
            # Create a new Terminal instance. Although not needed this is what is expected
            # and compatible to the non-multi-value behaviour.
            t = cls(child.label, content, child.parent, child.children, child.multi_value)
            t.content.extend(child.content) # add back original content
            return t
        return cls(child.label, content, child.parent, child.children, multi_value)

    def key(self) -> ByteString:
        l = bytes(self.label)
        parent = self.parent
        while isinstance(parent, Child):
            l = bytes(parent.label) + l
            parent = parent.parent
        return l

    def value(self) -> Any:
        return self.content

    def to_dot(self) -> str:
        s = super().to_dot()
        s += f"{self.dot_id()} [color=blue]\n"
        return s
