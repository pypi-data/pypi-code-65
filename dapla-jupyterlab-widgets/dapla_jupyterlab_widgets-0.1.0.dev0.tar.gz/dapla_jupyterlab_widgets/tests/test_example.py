#!/usr/bin/env python
# coding: utf-8

# Distributed under the terms of the Modified BSD License.

import pytest

from ..widget import ActiveNotebook


def test_example_creation_blank():
    w = ActiveNotebook()
    assert w.value == ''
