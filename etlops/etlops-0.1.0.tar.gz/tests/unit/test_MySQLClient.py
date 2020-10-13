from unittest.mock import Mock
from etlops.clients.rdbms import MySQLClient
from .db_client_utils import BaseDatabaseClientTestCase
from unittest import TestCase

mock_credentials = {
    "user": "blabla",
    "password": "yadayada",
    "host": "testing_host",
    "port": 3306,
    "database": "testing_database",
    "charset": "UTF-8",
}


class MySQLClientTest(BaseDatabaseClientTestCase, TestCase):
    def setUp(self):
        self.client = MySQLClient(mock_credentials)

    def test_context_manager_on_init(self):
        """
        This test should confirm that using the context manager on an instantiation
        of the class should work properly.
        """

        # Importing the client separately so we don't patch something on the import
        # being used everywhere else
        from etlops.clients.rdbms import MySQLClient as LocalMySQLClient

        mock_connect = Mock()
        mock_disconnect = Mock()
        LocalMySQLClient.connect = mock_connect
        LocalMySQLClient.disconnect = mock_disconnect

        mock_connect.assert_not_called()
        mock_disconnect.assert_not_called()

        with LocalMySQLClient(mock_credentials) as client:
            self.assertEqual(type(client), type(self.client))
            mock_connect.assert_called_once()
            mock_disconnect.assert_not_called()

        mock_connect.assert_called_once()
        mock_disconnect.assert_called_once()
