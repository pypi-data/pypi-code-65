from unittest import TestCase
from unittest.mock import Mock


class BaseDatabaseClientTestCase:
    """
    Helper test cases that should be applicable to all
    database clients. These tests assume that the database client
    will be instantiated and associated with the test instance
    and named `client`.
    """

    def test_context_manager_on_instance(self):
        """
        This test should confirm that using the context manager on an instance
        of the class should work properly.
        """
        # Overriding the actual methods to ensure we can test them
        mock_connect = Mock()
        mock_disconnect = Mock()

        self.client.connect = mock_connect
        self.client.disconnect = mock_disconnect

        mock_connect.assert_not_called()
        mock_disconnect.assert_not_called()

        with self.client:
            mock_connect.assert_called_once()
            mock_disconnect.assert_not_called()

        mock_connect.assert_called_once()
        mock_disconnect.assert_called_once()
