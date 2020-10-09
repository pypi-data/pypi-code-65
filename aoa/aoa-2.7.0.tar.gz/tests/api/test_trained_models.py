import pytest
import tempfile

from aoa.api.trained_model_api import TrainedModelApi
from aoa.api.model_api import ModelApi


def test_byom_models(setup):
    model_api = ModelApi(pytest.aoa_client)
    trained_model_api = TrainedModelApi(pytest.aoa_client)

    model = {
        "name": "My PMML",
        "description": "Test PMML Model",

        "externalModelAttributes": {
            "format": "PMML"
        }
    }

    model = model_api.save(model)

    trained_model = {
        "modelId": model["id"],
        "metadata": {
            "configuration": {
                "key1": "val1"
            }
        }
    }

    with tempfile.NamedTemporaryFile(delete=False) as fp:
        fp.write(b'Hello world!')

    trained_model_api.save(trained_model, [fp.name])

