from click.testing import CliRunner
from tests.utilities import create_local_schema_client

from grid import cli
from grid.client import Grid

CREDENTIAL_ID = 'test-credential'
RUNNER = CliRunner()


# Monkey patches the getting of credentials
def monkey_patch_get_credentials(self):
    return {
        'getUserCredentials': [{
            'credentialId': CREDENTIAL_ID,
            'provider': 'aws',
            'defaultCredential': True
        }]
    }


# Monkey patches the check for tokens
def monkey_patch_token_check(self):
    return {'checkUserGithubToken': {'hasValidToken': True}}


#  Monkey patch the client.
def monkey_patch_no_creds(self):
    return {'getUserCredentials': []}


#  Monkey patches the GraphQL client to read from a local schema.
def monkey_patch_client(self):
    self.client = create_local_schema_client()


def test_train_fails_with_no_arguments(monkeypatch):
    """grid train without arguments fails"""
    monkeypatch.setattr(Grid, '_init_client', monkey_patch_client)
    monkeypatch.setattr(Grid, 'get_credentials', monkey_patch_get_credentials)
    monkeypatch.setattr(Grid, '_check_user_github_token',
                        monkey_patch_token_check)

    result = RUNNER.invoke(cli.train, [])
    assert result.exit_code == 2
    assert result.exception


def test_train_fails_with_no_credentials(monkeypatch):
    """grid train fails if user has no credentials."""
    monkeypatch.setattr(Grid, 'get_credentials', monkey_patch_no_creds)
    monkeypatch.setattr(Grid, '_set_local_credentials', lambda x: True)
    monkeypatch.setattr(Grid, '_check_user_github_token',
                        monkey_patch_token_check)

    result = RUNNER.invoke(cli.train, ['--', 'tests/data/script.py'])

    assert result.exit_code == 1
    assert result.exception


def test_train_fails_if_credentials_dont_exist(monkeypatch):
    """grid train fails if credentials don't exist for user."""
    monkeypatch.setattr(Grid, '_set_local_credentials', lambda x: True)
    monkeypatch.setattr(Grid, '_check_user_github_token',
                        monkey_patch_token_check)

    result = RUNNER.invoke(cli.train, [
        '--grid_credential', 'test-fail', '--grid_cpus', 1, '--',
        'tests/data/script.py'
    ])

    assert result.exit_code == 1
    assert result.exception


def test_train_fails_if_description_is_too_long(monkeypatch):
    """grid train fails if description is too long."""
    description = 201 * '-'  #  200 characters is the limit.
    result = RUNNER.invoke(cli.train, [
        '--grid_description', description, '--grid_credential', CREDENTIAL_ID,
        '--grid_cpus', 1, '--', 'tests/data/script.py'
    ])
    assert result.exit_code == 2
    assert result.exception


def test_train_fails_if_run_name_fails_validation(monkeypatch):
    """grid train fails if run name does not match validation requirements."""
    run_name = "RUN"  # capital letters not allowed in run name
    monkeypatch.setattr(Grid, '_init_client', monkey_patch_client)
    monkeypatch.setattr(Grid, 'get_credentials', monkey_patch_get_credentials)
    monkeypatch.setattr(Grid, '_set_local_credentials', lambda x: True)
    monkeypatch.setattr(Grid, '_check_user_github_token',
                        monkey_patch_token_check)

    result = RUNNER.invoke(cli.train, [
        '--grid_credential',
        CREDENTIAL_ID,
        '--grid_name',
        run_name,
        '--grid_cpus',
        1,
        '--',
        'tests/data/script.py',
    ])
    assert result.exit_code == 2
    assert result.exception


def test_train(monkeypatch):
    """grid train returns 0 exit code"""
    monkeypatch.setattr(Grid, '_init_client', monkey_patch_client)
    monkeypatch.setattr(Grid, 'get_credentials', monkey_patch_get_credentials)
    monkeypatch.setattr(Grid, '_set_local_credentials', lambda x: True)
    monkeypatch.setattr(Grid, '_check_user_github_token',
                        monkey_patch_token_check)

    result = RUNNER.invoke(cli.train, [
        '--grid_credential', CREDENTIAL_ID, '--ignore_warnings', '--',
        'tests/data/script.py'
    ])

    assert result.exit_code == 0
    assert not result.exception


# TODO: Finish this test.
# def test_check_user_github_token(monkeypatch):
#     """Checks for the GH Token check."""
#     def monkey_patch_client(self):
#         self.client = create_local_schema_client()

#     monkeypatch.setattr(Grid, '_init_client', monkey_patch_client)
#     Grid._check_user_github_token()
