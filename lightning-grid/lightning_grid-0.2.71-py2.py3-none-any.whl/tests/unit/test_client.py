import os
import csv
import glob
import json
import click
import unittest

from pathlib import Path
from tests.utilities import create_local_schema_client

from grid.client import env
from grid.client import Grid
from grid.types import WorkflowType, ObservableType
from grid.exceptions import TrainError


def monkey_patch_observables():
    """Monkey patches the observables factory."""
    class MonkeyPatchedObservable:
        key = 'getRuns'

        def get(self, *args, **kwarrgs):
            return {
                self.key: [{
                    'columnn': 'value'
                }, {
                    'column_fail_a': []
                }, {
                    'column_fail_b': {}
                }]
            }

    return {
        ObservableType.EXPERIMENT: MonkeyPatchedObservable,
        ObservableType.RUN: MonkeyPatchedObservable,
        ObservableType.CLUSTER: MonkeyPatchedObservable,
    }


# Monkey patches the check for tokens
def monkey_patch_token_check(self):
    return {'checkUserGithubToken': {'hasValidToken': True}}


class GridClientTestCase(unittest.TestCase):
    """Unit tests for the Grid class."""
    @classmethod
    def setUpClass(cls):
        #  Monkey patches the GraphQL client to read from a local schema.
        def monkey_patch_client(self):
            self.client = create_local_schema_client()

        #  skipcq: PYL-W0212
        Grid._init_client = monkey_patch_client
        Grid._check_user_github_token = monkey_patch_token_check

        cls.creds_path = 'tests/data/credentials.json'
        cls.grid_header_keys = ['X-Grid-User', 'X-Grid-Key']

        cls.train_kwargs = {
            'config': 'test-config',
            'kind': WorkflowType.SCRIPT,
            'run_name': 'test-run',
            'run_description': 'test description',
            'entrypoint': 'test_file.py',
            'script_args': ['--learning_rate', '0.001']
        }

    def remove_env(self):
        #  Makes sure that the GRID_CREDENTIAL_PATH is not set
        if os.getenv('GRID_CREDENTIAL_PATH'):
            del os.environ['GRID_CREDENTIAL_PATH']

    def remove_status_files(self):
        # path = 'test/data/'
        for e in ['csv', 'json']:
            for f in glob.glob(f'*.{e}'):
                os.remove(f)

    def setUp(self):
        self.remove_env()
        self.remove_status_files()

    def tearDown(self):
        self.remove_env()

        #  Removes test credentials added to home path.
        P = Path.home().joinpath(self.creds_path)
        if P.exists():
            P.unlink(missing_ok=True)

        self.remove_status_files()

    def test_client_local_path(self):
        """Client with local credentials path initializes correctly"""

        G = Grid(credential_path=self.creds_path, load_local_credentials=False)
        for key in self.grid_header_keys:
            assert key in G.headers.keys()

    def test_client_loads_credentials_from_env_var(self):
        """Client loads credentials path from env var"""
        os.environ['GRID_CREDENTIAL_PATH'] = self.creds_path
        G = Grid()
        for key in self.grid_header_keys:
            assert key in G.headers.keys()

        os.environ['GRID_CREDENTIAL_PATH'] = 'fake-path'
        with self.assertRaises(click.ClickException):
            Grid()

        self.remove_env()

    def test_client_raises_exception_if_creds_path_not_found(self):
        """Client raises exception if credentials path not found"""
        credentials_path = 'tests/data/foo.json'
        with self.assertRaises(click.ClickException):
            Grid(credential_path=credentials_path)

    def test_nested_path_is_parsed_correctly(self):
        """Tests that we can add the Git root path to a script"""
        result = Grid._add_git_root_path(entrypoint='foo.py')
        path_elems = result.split(os.path.sep)
        self.assertListEqual(path_elems[-2:], ['grid-cli', 'foo.py'])

    def test_client_loads_credentials_from_default_path(self):
        """Client loads credentials from default path"""
        test_path = 'tests/data/credentials.json'
        with open(test_path) as f:
            credentials = json.load(f)

        #  Let's create a credentials file in the home
        #  directory.
        creds_name = 'test_credentials.json'
        P = Path.home().joinpath(creds_name)
        with P.open('w') as f:
            json.dump(credentials, f)

        Grid.grid_credentials_path = creds_name
        G = Grid()

        assert G.credentials.get('UserID') == credentials['UserID']

    def test_client_raises_error_if_no_creds_available(self):
        """Client loads credentials from default path"""
        test_path = 'tests/data/foo.json'
        Grid.grid_credentials_path = test_path

        with self.assertRaises(click.ClickException):
            Grid()

    #  NOTE: there's a race condition here with the env
    #  var. Let's leave this named this way.
    def test_a_client_local_init(self):
        """Client init without local credentials leaves headers unchanged"""

        assert not os.getenv('GRID_CREDENTIAL_PATH')

        G = Grid(load_local_credentials=False)
        for key in self.grid_header_keys:
            assert key not in G.headers.keys()

    def test_train(self):
        """Grid().train() executes a training operation correctly."""
        G = Grid(credential_path=self.creds_path, load_local_credentials=False)
        G.train(**self.train_kwargs)

    def test_train_raises_exception_blueprint(self):
        """
        Grid().train() raises exception when attempting to
        train a blueprint.
        """
        G = Grid(credential_path=self.creds_path, load_local_credentials=False)
        with self.assertRaises(TrainError):
            G.train(**{**self.train_kwargs, 'kind': WorkflowType.BLUEPRINT})

    def test_train_raises_exception_if_query_fails(self):
        class MonkeyPatchClient:
            def execute(self, *args, **kwargs):
                raise Exception("{'message': 'test exception'}")

        G = Grid(credential_path=self.creds_path, load_local_credentials=False)
        G.client = MonkeyPatchClient()
        with self.assertRaises(click.ClickException):
            G.train(**self.train_kwargs)

    def test_status_returns_results(self):
        """Grid().status() returns a dict results."""
        G = Grid(credential_path=self.creds_path, load_local_credentials=False)

        G.available_observables = monkey_patch_observables()
        results = G.status()
        assert isinstance(results, dict)

    def test_status_generates_output_files(self):
        """Grid().status() generates output files."""
        G = Grid(credential_path=self.creds_path, load_local_credentials=False)

        G.available_observables = monkey_patch_observables()

        #  Tests exporting.
        extensions = ['csv', 'json']
        for e in extensions:
            G.status(export=e)
            files = [*glob.glob(f'*.{e}')]
            assert len(files) == 1

            #  Test that lists or dict columns are not exported to CSV.
            if e == 'csv':
                with open(files[0], 'r') as f:
                    data = [*csv.DictReader(f)]
                    assert 'column_fail_a' not in data[0].keys()
                    assert 'column_fail_b' not in data[0].keys()

    def test_download_artifacts(self):
        """Grid().download_experiment_artifacts() does not fail"""
        experiment_id = 'test-experiment-exp0'
        G = Grid(credential_path=self.creds_path, load_local_credentials=False)
        G.download_experiment_artifacts(experiment_id=experiment_id,
                                        download_dir='tests/data')
