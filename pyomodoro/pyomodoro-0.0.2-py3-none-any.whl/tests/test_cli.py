import importlib.resources
import os

from click.testing import CliRunner

from pyomodoro.cli import start
import pyomodoro.resources
import pyomodoro.tests.resources


class TestStart:
    runner = CliRunner()

    def test_float_intervals_are_invalid(self):
        result = self.runner.invoke(start, ['-p', '.5'])
        assert result.exit_code != 0

    def test_command_succeeds(self):
        result = self.runner.invoke(start, ['-p', '0', '-sb', '0', '-lb', '0'], input='N')
        assert result.exit_code == 0

    def test_specified_config_file_is_used(self):
        with importlib.resources.path(pyomodoro.tests.resources, 'good_config.yml') as config_file:
            result = self.runner.invoke(start, ['-d', '-f', str(config_file)])
        assert result.exit_code == 0
        assert 'pomodoro_length: 15' in result.output
        assert 'short_break_length: 2' in result.output
        assert 'long_break_length: 3' in result.output

    def test_config_file_can_be_overridden(self):
        with importlib.resources.path(pyomodoro.tests.resources, 'good_config.yml') as config_file:
            result = self.runner.invoke(start, ['-d', '-p', '4', '-f', str(config_file)])
        assert result.exit_code == 0
        assert 'pomodoro_length: 4' in result.output
        assert 'short_break_length: 2' in result.output
        assert 'long_break_length: 3' in result.output

    def test_config_file_with_hanging_quote(self):
        with importlib.resources.path(pyomodoro.tests.resources, 'hanging_quote_config.yml') as config_file:
            result = self.runner.invoke(start, ['-d', '-f', str(config_file)])
        assert result.exit_code != 0

    def test_config_file_with_interval_values(self):
        with importlib.resources.path(pyomodoro.tests.resources, 'interval_values_config.yml') as config_file:
            result = self.runner.invoke(start, ['-d', '-f', str(config_file)])
        assert result.exit_code == 0
        assert 'pomodoro_length: 45' in result.output
        assert 'short_break_length: 12' in result.output
        assert 'long_break_length: 33' in result.output

    def test_config_file_with_nested_config(self):
        with importlib.resources.path(pyomodoro.tests.resources, 'nested_config.yml') as config_file:
            result = self.runner.invoke(start, ['-d', '-f', str(config_file)])
        assert result.exit_code == 0
        assert 'nested_config.yml' in result.output
        assert '~/.pyomodoro2' not in result.output
        assert 'pomodoro_length: 65' in result.output
        assert 'short_break_length: 35' in result.output
        assert 'long_break_length: 44' in result.output


def test_icon_ico_exists():
    with importlib.resources.path(pyomodoro.resources, 'pyomodoro.ico') as icon_path:
        assert os.path.isfile(str(icon_path))


def test_icon_png_exists():
    with importlib.resources.path(pyomodoro.resources, 'pyomodoro.png') as icon_path:
        assert os.path.isfile(str(icon_path))
