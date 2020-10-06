import json

import pytest

from cfloader.loader import Loader
import tests.models as models
from tests.models import DummyModelWithParams

@pytest.fixture
def model_config():
    return {"model": {"model_name": "Test"}, "epochs": 10}


def test_loader_can_be_instantiated(model_config):
    loader = Loader(model_config)

    assert loader.config == model_config


def test_loader_can_retrieve_values_with_simple_keys(model_config):
    loader = Loader(model_config)

    assert loader.load("epochs") == 10


def test_loader_can_retrieve_values_with_compound_keys(model_config):
    loader = Loader(model_config)

    assert loader.load("model") == model_config["model"]
    assert loader.load("model.model_name") == "Test"


def test_loader_can_instantiate_class_as_string():
    loader = Loader({"model": "DummyModelWithoutParams"})

    model = loader.load("model", as_class=True, package="tests.models")

    assert isinstance(model, models.DummyModelWithoutParams)


def test_loader_can_instantiate_class_as_dict():
    loader = Loader({"model": {"model_name": "DummyModelWithoutParams"}})

    model = loader.load("model", as_class=True, package="tests.models")

    assert isinstance(model, models.DummyModelWithoutParams)


def test_loader_can_instantiate_class_with_params():
    loader = Loader(
        {
            "model": {
                "model_name": "DummyModelWithParams",
                "epochs": 10,
                "batch_size": 60,
            }
        }
    )

    model: DummyModelWithParams = loader.load(
        "model", as_class=True, package="tests.models"
    )

    assert isinstance(model, DummyModelWithParams)
    assert model.epochs == 10
    assert model.batch_size == 60

def test_nonexistent_key_returns_none():
    loader = Loader(
        {
            "model": {
                "model_name": "DummyModelWithParams",
                "epochs": 10,
                "batch_size": 60,
            }
        }
    )

    assert loader.load("embedding") == None

def test_absolute_classpath_is_resolved_when_loading_class():
    loader = Loader(
        {
            "model": {
                "model_name": "tests.models.DummyModelWithParams",
                "epochs": 10,
                "batch_size": 60,
            }
        }
    )

    model: DummyModelWithParams = loader.load(
        "model", as_class=True
    )

    assert isinstance(model, DummyModelWithParams)
    assert model.epochs == 10
    assert model.batch_size == 60

def test_relative_classpath_is_resolved_when_loading_class():
    loader = Loader(
        {
            "model": {
                "model_name": "DummyModelWithParams",
                "epochs": 10,
                "batch_size": 60,
            }
        }
    )

    model: DummyModelWithParams = loader.load(
        "model", as_class=True, package=".models"
    )

    assert isinstance(model, DummyModelWithParams)
    assert model.epochs == 10
    assert model.batch_size == 60

def test_class_is_loaded_from_calling_package_if_none_specified():
    loader = Loader(
        {
            "model": {
                "model_name": "DummyModelWithParams",
                "epochs": 10,
                "batch_size": 60,
            }
        }
    )

    model: DummyModelWithParams = loader.load(
        "model", as_class=True
    )

    assert isinstance(model, DummyModelWithParams)
    assert model.epochs == 10
    assert model.batch_size == 60

def test_class_is_not_loaded_if_name_is_not_specified():
    loader = Loader(
        {
            "model": {
                "model_nam": "DummyModelWithParams",
                "epochs": 10,
                "batch_size": 60,
            }
        }
    )

    with pytest.raises(KeyError):
        model: DummyModelWithParams = loader.load(
            "model", as_class=True, package=".models"
        )

def test_nested_classes_are_loaded():
    loader = Loader({
        "embedding": {
            "embedding_name": "DummyEmbedding",
            "vocab_size": 500,
            "dim": 50
        },
        "dependencies": {
            "primary": {
                "dependencies.primary_name": "DummyDependency",
                "secondary_dependency": {
                    "load": True,
                    "key": "dependencies.secondary",
                    "as_class": True
                }
            },
            "secondary": {
                "dependencies.secondary_name": "DummyDependency",
                "secondary_dependency": None
            }
        },
        "model": {
            "model_name": "DummyModelWithDependency",
            "embedding": {
                "load": True,
                "key": "embedding",
                "as_class": True
            },
            "dependency": {
                "load": True,
                "key": "dependencies.primary",
                "as_class": True
            },
            "embedding_size": {
                "load": True,
                "key": "embedding.dim"
            }
        }
    })

    model: DummyModelWithDependency = loader.load(
        "model", as_class=True, package=".models"
    )
    
    assert isinstance(model, models.DummyModelWithDependency)
    assert isinstance(model.embedding, models.DummyEmbedding)
    assert isinstance(model.dependency, models.DummyDependency)
    assert isinstance(model.dependency.dependency, models.DummyDependency)

    assert model.dependency.dependency.dependency == None
    
    assert model.embedding_size == model.embedding.dim