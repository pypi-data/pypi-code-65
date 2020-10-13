"""test_metadata module"""

import sys
import unittest
import json
from matatika.metadata import Metadata, Dataset

sys.path.append('../src/')

EMPTY = ''


class TestMetadata(unittest.TestCase):
    """Class containing Metadata unit tests"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_empty_dataset(self):
        """
        Creates an empty dataset, converts it to JSON and then back to a Python object

        Expects each field value to be an empty string
        """

        dataset = Dataset()
        data = json.loads(dataset.to_json())

        self.assertIs(data['alias'], EMPTY)
        self.assertIs(data['workspace_id'], EMPTY)
        self.assertIs(data['category'], EMPTY)
        self.assertIs(data['title'], EMPTY)
        self.assertIs(data['description'], EMPTY)
        self.assertIs(data['questions'], EMPTY)
        self.assertIs(data['rawData'], EMPTY)
        self.assertIs(data['visualisation'], EMPTY)
        self.assertIs(data['query'], EMPTY)

    def test_dataset_with_value(self):
        """
        Creates a populated dataset, converts it to JSON and then back to a Python object

        Expects each field to have the value that was initially set
        """

        dataset = Dataset()
        dataset.dataset_id = 'test1'
        dataset.workspace_id = 'test2'
        dataset.category = 'test3'
        dataset.title = 'test4'
        dataset.description = 'test5'
        dataset.questions = 'test6'
        dataset.rawData = 'test7'
        dataset.visualisation = 'test8'
        dataset.query = 'test9'

        data = json.loads(dataset.to_json())
        self.assertEqual(data['dataset_id'], 'test1')
        self.assertEqual(data['workspace_id'], 'test2')
        self.assertEqual(data['category'], 'test3')
        self.assertEqual(data['title'], 'test4')
        self.assertEqual(data['description'], 'test5')
        self.assertEqual(data['questions'], 'test6')
        self.assertEqual(data['rawData'], 'test7')
        self.assertEqual(data['visualisation'], 'test8')
        self.assertEqual(data['query'], 'test9')

    # @unittest.skip('TEMP')
    def test_all_should_be_empty_apart_from_dataset_id(self):
        """
        Creates a dataset with 'dataset-id' populated, converts it to JSON and then back to a
        Python object

        Expects the 'dataset-id' field to have the value that was initially set
        """

        dataset = Dataset()
        dataset.dataset_id = 'test-dataset'
        data = json.loads(dataset.to_json())
        self.assertEqual(data['dataset_id'], 'test-dataset')
        self.assertEqual(data['workspace_id'], EMPTY)
        self.assertEqual(data['category'], EMPTY)
        self.assertEqual(data['title'], EMPTY)
        self.assertEqual(data['description'], EMPTY)
        self.assertEqual(data['questions'], EMPTY)
        self.assertEqual(data['rawData'], EMPTY)
        self.assertEqual(data['visualisation'], EMPTY)
        self.assertEqual(data['query'], EMPTY)

    # @unittest.skip('TEMP')
    def test_should_return_json(self):
        """
        Creates and populates a Metadata object, converts it to JSON

        Expects a JSON string to be returned
        """

        metadata = Metadata(
            dataset_id='dataset_id',
            alias='alias',
            workspace_id='workspace_id',
            category='category',
            title='title',
            description='description',
            questions='questions',
            rawData='rawData',
            visualisation='visualisation',
            metadata='metadata',
            query='query')

        dataset_str = '{' +                         \
            '"dataset_id": "dataset_id", ' +        \
            '"alias": "alias", ' +                  \
            '"workspace_id": "workspace_id", ' +    \
            '"category": "category", ' +            \
            '"title": "title", ' +      \
            '"description": "description", ' +      \
            '"questions": "questions", ' +          \
            '"rawData": "rawData", ' +            \
            '"visualisation": "visualisation", ' +  \
            '"metadata": "metadata", ' +  \
            '"query": "query"' +                    \
            '}'

        self.assertEqual(metadata.to_json(), dataset_str)


if __name__ == '__main__':
    unittest.main()
