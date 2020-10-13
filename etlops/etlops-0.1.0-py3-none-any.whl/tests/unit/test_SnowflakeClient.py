import unittest
from unittest.mock import Mock
from itertools import product
from etlops.clients.mpp import SnowflakeClient
from pandas import DataFrame
from .db_client_utils import BaseDatabaseClientTestCase
from unittest import TestCase

MockCredentials = {
    "user": "blabla",
    "account": "bloblo",
    "password": "yadayada",
    "insecure_mode": False,
}


class SnowflakeClientTest(BaseDatabaseClientTestCase, TestCase):
    valid_warehouse_states = ("STARTED", "SUSPENDING", "SUSPENDED")

    def setUp(self):
        self.client = SnowflakeClient(config=MockCredentials)
        self.client.dml_query = Mock()
        self.client.select_query = Mock()

    def test_check_warehouse_state_dispatchs_correct_warehouse_state(self):
        for valid_warehouse_state in self.valid_warehouse_states:
            self.client.select_query.return_value = DataFrame(
                {
                    "name": "MEDIUM_QUERY",
                    "state": valid_warehouse_state,
                    "type": None,
                    "size": None,
                },
                index=[0],
            )
            self.assertTrue(
                self.client._SnowflakeClient__check_warehouse_state(
                    warehouse="medium_query"
                )
                in self.valid_warehouse_states
            )

    def test_AlterWarehouse_resumes_and_suspends_only_when_it_should(self,):
        alter_warehouse_test_params = tuple(
            [
                Pair
                for Pair in product(
                    ["STARTED", "SUSPENDED", "SUSPENDING"], ["resume", "suspend"]
                )
            ]
        )
        for warehouse_status, action in alter_warehouse_test_params:
            self.client._SnowflakeClient__check_warehouse_state = Mock(
                return_value=warehouse_status
            )
            self.client.alter_warehouse(warehouse="MEDIUM_QUERY", action=action)
            if (
                action == "suspend"
                and warehouse_status not in ("SUSPENDED", "SUSPENDING")
            ) or (
                action == "resume" and warehouse_status in ("SUSPENDED", "SUSPENDING")
            ):
                self.client.dml_query.assert_called_with(
                    "Alter warehouse {warehouse} {ACTION};".format(
                        warehouse="MEDIUM_QUERY", ACTION=action
                    )
                )
                self.client.dml_query.reset_mock()
            else:
                self.client.dml_query.assert_not_called()

    def test_context_manager_on_init(self):
        """
        This test should confirm that using the context manager on an instantiation
        of the class should work properly.
        """
        # Importing the client separately so we don't patch something on the import
        # being used everywhere else
        from etlops.clients.mpp import SnowflakeClient as LocalSnowflakeClient

        mock_connect = Mock()
        mock_disconnect = Mock()
        LocalSnowflakeClient.connect = mock_connect
        LocalSnowflakeClient.disconnect = mock_disconnect

        mock_connect.assert_not_called()
        mock_disconnect.assert_not_called()

        with LocalSnowflakeClient(MockCredentials) as client:
            self.assertEqual(type(client), type(self.client))
            mock_connect.assert_called_once()
            mock_disconnect.assert_not_called()

        mock_connect.assert_called_once()
        mock_disconnect.assert_called_once()
