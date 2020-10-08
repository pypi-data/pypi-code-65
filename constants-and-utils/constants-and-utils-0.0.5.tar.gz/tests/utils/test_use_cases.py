from unittest import TestCase
from constants_and_utils.utils.use_cases import (
    Response,
    ExportResponse,
    DataResponse,
)


class TestResponse(TestCase):

    def test_ok(self):
        expected = {'errors': None, 'http_code': 200, 'message': 'OK'}
        result = Response(
            http_code=200,
            message='OK'
            )

        self.assertEqual(result.__json__(), expected)


class TestDataResponsee(TestCase):

    def test_ok(self):
        expected = {
            'errors': None,
            'http_code': 200,
            'message': 'OK',
            'data': {}
        }

        result = DataResponse(
            http_code=200,
            message='OK',
            data={}
        )

        self.assertEqual(result.__json__(), expected)


class TestExportResponse(TestCase):

    def test_ok(self):
        expected = {
            'errors': None, 'http_code': 200, 'message': 'OK',
            'file_name': 'file.csv'
            }

        result = ExportResponse(
            http_code=200,
            message='OK',
            file_name='file.csv'
            )

        self.assertEqual(result.__json__(), expected)
