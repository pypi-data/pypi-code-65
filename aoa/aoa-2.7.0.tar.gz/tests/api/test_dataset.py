import pytest
import uuid
from aoa.api.dataset_api import DatasetApi
from aoa.api.dataset_template_api import DatasetTemplateApi


def _skip_generated_fields(dataset):
    keys_to_remove = ('id', 'ownerId', 'createdAt', '_links', 'projectId')
    for k in keys_to_remove:
        dataset.pop(k, None)
    return dataset


def test_dataset(setup):

    dataset_template_api = DatasetTemplateApi(pytest.aoa_client)
    dataset_template_definition = {
        "name": str(uuid.uuid4()),
        "description": "dataset testing template",
        "templateBody": {
            "common": {},
            "train": {},
            "evaluate": {}
        }
    }

    dataset_template_rtn = dataset_template_api.save(dataset_template_definition)

    dataset_api = DatasetApi(pytest.aoa_client)
    before_count = len(dataset_api)

    dataset_definition = {
        "name": str(uuid.uuid4()),
        "description": "adding sample dataset",
        "datasetTemplateId" : dataset_template_rtn['id'],
        "scope": "train",
        "metadata": {
            "url": "http://nrvis.com/data/mldata/pima-indians-diabetes.csv",
            "test_split": "0.2"
        }
    }

    dataset_rtn = dataset_api.save(dataset_definition)

    after_count = len(dataset_api)
    assert ( before_count + 1 == after_count), "save dataset...failed"

    dataset_rtn_by_id = dataset_api.find_by_id(dataset_id=dataset_rtn['id'])
    assert (_skip_generated_fields(dataset_rtn_by_id) == dataset_definition), "validate new dataset...failed"

    dataset_by_name = dataset_api.find_by_name(dataset_name=dataset_definition["name"])
    assert (_skip_generated_fields(dataset_by_name) == dataset_definition), "find dataset by name...failed"

    dataset_rtn_by_id = dataset_api.find_by_id(dataset_id=str(uuid.uuid4()))
    assert (dataset_rtn_by_id is None), "validate missing resouce... failed"


