"""
Tests for the hello() function.
"""

from logger import get_log


def test_hello_without_name():
    """Test with no parameter."""
    assert get_log() is not None
