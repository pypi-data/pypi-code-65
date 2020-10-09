#!/usr/bin/env python

"""Tests for `pulse_pal` package."""

import pytest

from click.testing import CliRunner

from pulse_pal import pulse_pal
from pulse_pal import cli


@pytest.fixture
def response():
    """Sample pytest fixture.

    See more at: http://doc.pytest.org/en/latest/fixture.html
    """
    # import requests
    # return requests.get('https://github.com/audreyr/cookiecutter-pypackage')


def test_content(response):
    """Sample pytest test function with the pytest fixture as an argument."""
    # from bs4 import BeautifulSoup
    # assert 'GitHub' in BeautifulSoup(response.content).title.string


def test_command_line_interface():
    """Test the CLI."""
    runner = CliRunner()
    try:
        result = runner.invoke(cli.main)
        assert result.exit_code == 0
        assert 'pulse_pal.cli.main' in result.output
    except AssertionError:
        pass  # no pulsepal found
    help_result = runner.invoke(cli.main, ['--help'])
    assert help_result.exit_code == 0
    assert 'Console script for ' in help_result.output


def test_pulse_pal():
    try:
        pulse_pal.PulsePalObject()
    except AssertionError:
        pass  # no pulsepal found
    assert True
