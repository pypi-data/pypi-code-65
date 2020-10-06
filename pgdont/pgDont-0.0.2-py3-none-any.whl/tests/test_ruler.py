from click.testing import CliRunner

from pgdont import cli

from .database_test_case import DatabaseTestCase


class CliRulerTestCase(DatabaseTestCase):

    def test_it_runs_in_default_mode(self) -> None:
        runner = CliRunner()
        result = runner.invoke(cli, ['--dsn', self._postgres.url()])

        self.assertEqual(result.exit_code, 0)
