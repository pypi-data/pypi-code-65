#!/usr/bin/env python

## Standard Library
import logging

## TTILS
from .conf import *
from .meta import Node
from .validation import *

__all__ = ['A', 'B']

class A(Node):
    parent = SizedRegexString(maxlen=20, pattern=r"^[^0-9]")
    child = SizedString(maxlen=20)
    edges = NonNegativeInteger()


class B(Node):
    ingress = NonNegativeInteger()
    egress = NonNegativeInteger()
    payload = SizedRegexString(maxlen=20, pattern=r"[A-Za-z_ ]+$")
