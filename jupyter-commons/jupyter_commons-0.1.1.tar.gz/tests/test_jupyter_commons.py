# -*- coding: utf-8 -*-

"""Tests for `jupyter_commons` package."""
import jupyter_commons.output as jc_out


def test_colorize():
    """Test colorization of string."""
    assert "lightblue" in jc_out.colorize("some message", color="lightblue")
    assert "darkgreen" in jc_out.colorize("some message", color="darkgreen")


def test_msg_red():
    """Test colorization of string."""
    assert "red" in jc_out.msg_red("some message")


def test_msg_green():
    """Test colorization of string."""
    assert "green" in jc_out.msg_green("some message")


def test_msg_blue():
    """Test colorization of string."""
    assert "blue" in jc_out.msg_blue("some message")


def test_highlight():
    """Test highlighting of string."""
    assert "background:yellow" in jc_out.highlight("some message")
    assert "background:green" in jc_out.highlight("some message", color='green')
