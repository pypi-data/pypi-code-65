# coding: utf-8

"""
    TileDB Storage Platform API

    TileDB Storage Platform REST API  # noqa: E501

    The version of the OpenAPI document: 2.0.4
    Generated by: https://openapi-generator.tech
"""


from __future__ import absolute_import

import unittest

import rest_api
from tiledb.cloud.rest_api.api.notebook_api import NotebookApi  # noqa: E501
from tiledb.cloud.rest_api.rest import ApiException


class TestNotebookApi(unittest.TestCase):
    """NotebookApi unit test stubs"""

    def setUp(self):
        self.api = tiledb.cloud.rest_api.api.notebook_api.NotebookApi()  # noqa: E501

    def tearDown(self):
        pass

    def test_get_notebook_server_status(self):
        """Test case for get_notebook_server_status"""
        pass

    def test_shutdown_notebook_server(self):
        """Test case for shutdown_notebook_server"""
        pass


if __name__ == "__main__":
    unittest.main()
