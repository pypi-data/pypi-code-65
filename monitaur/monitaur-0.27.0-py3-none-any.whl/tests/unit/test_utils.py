from pathlib import Path

import boto3
import joblib
import pytest
from monitaur.exceptions import CustomInfluencesError, FileError, MetricsError
from monitaur.virgil.alibi.tabular import AnchorTabular

from monitaur.utils import (  # isort:skip
    generate_anchors,
    upload_file_to_s3,
    valid_model,
    validate_influences,
    validate_drift_metrics,
    validate_bias_metrics,
)


def test_valid_model():
    assert valid_model(".pickle", "tabular")
    assert valid_model(".pkl", "tabular")
    assert valid_model(".p", "tabular")
    assert valid_model(".sav", "tabular")
    assert valid_model(".h5", "image")
    assert valid_model(".pkl", "image")
    assert valid_model(".p", "image")
    assert valid_model(".sav", "image")

    with pytest.raises(FileError) as excinfo:
        valid_model(".h5", "tabular")
    assert (
        "Invalid model. Acceptable files: '.joblib', '.pickle', '.pkl.', '.p', '.sav'."
        == excinfo.value.message
    )

    with pytest.raises(FileError) as excinfo:
        valid_model("", "image")
    assert (
        "Invalid model. Acceptable files: '.joblib', '.tar', '.h5', '.pkl.', '.p', '.sav'."
        == excinfo.value.message
    )


def test_generate_anchors(mocker, training_data):
    mocker.patch.object(
        joblib, "load", return_value=b"Image-Base-64-encoded-return-data"
    )
    mocker.patch.object(AnchorTabular, "__init__", return_value=None)
    mocker.patch.object(AnchorTabular, "fit")

    assert generate_anchors(
        ".joblib",
        "job.joblib",
        [
            "Pregnancies",
            "Glucose",
            "BloodPressure",
            "SkinThickness",
            "Insulin",
            "BMI",
            "DiabetesPedigreeF",
            "Age",
        ],
        training_data,
        1,
    )


def test_upload_file_to_s3(mocker, training_data):
    boto_mock = mocker.patch.object(boto3, "client")
    mocker.patch("builtins.open")

    assert upload_file_to_s3(
        1,
        0.1,
        "job.joblib",
        {
            "aws_access_key": "not real",
            "aws_secret_key": "not real",
            "aws_region": "not real",
            "aws_bucket_name": "not real",
        },
    )

    assert boto_mock.call_count == 1


@pytest.mark.parametrize(
    "model_influences, model_class, custom_influences, processing_files",
    [
        ("custom-dict", "tabular", {}, ["processing.pickle"]),
        ("custom-image", "tabular", Path("foo.jpeg"), ["processing.pickle"]),
        ("anchors", "tabular", None, []),
        (None, "tabular", None, []),
        ("custom-dict", "image", {}, ["processing.pickle"]),
        ("custom-image", "image", Path("foo.jpeg"), ["processing.pickle"]),
        ("anchors", "image", None, []),
        (None, "image", None, ["processing.pickle"]),
        ("custom-dict", "nlp", {}, ["processing.pickle"]),
        ("custom-image", "nlp", Path("foo.jpeg"), ["processing.pickle"]),
        ("anchors", "nlp", None, []),
        (None, "nlp", None, ["processing.pickle"]),
    ],
)
def test_validate_influences_valid(
    model_influences, model_class, custom_influences, processing_files
):
    assert validate_influences(
        model_influences, model_class, custom_influences, processing_files
    )


@pytest.mark.parametrize(
    "model_influences, model_class, custom_influences, processing_files, value",
    [
        ("custom-dict", "tabular", "foo.png", ["processing.pickle"], "a dict"),
        ("custom-image", "tabular", {}, ["processing.pickle"], "a file path"),
        ("anchors", "tabular", {}, [], "None"),
        (None, "tabular", {}, ["processing.pickle"], "None"),
        ("custom-dict", "image", "foo.png", ["processing.pickle"], "a dict"),
        ("custom-image", "image", {}, ["processing.pickle"], "a file path"),
        ("anchors", "image", {}, [], "None"),
        (None, "image", {}, ["processing.pickle"], "None"),
        ("custom-dict", "nlp", "foo.png", ["processing.pickle"], "a dict"),
        ("custom-image", "nlp", {}, ["processing.pickle"], "a file path"),
        ("anchors", "nlp", {}, [], "None"),
        (None, "nlp", {}, ["processing.pickle"], "None"),
    ],
)
def test_validate_influences_invalid(
    model_influences, model_class, custom_influences, processing_files, value
):
    with pytest.raises(CustomInfluencesError) as excinfo:
        validate_influences(
            model_influences, model_class, custom_influences, processing_files
        )
    assert (
        f"When model.influences is {model_influences}, custom_influences must be {value}."
        == excinfo.value.message
    )


@pytest.mark.parametrize(
    "model_influences, model_class, custom_influences, processing_files",
    [
        ("anchors", "tabular", {}, ["processing.pickle"]),
        ("anchors", "image", {}, ["processing.pickle"]),
        ("anchors", "nlp", {}, ["processing.pickle"]),
    ],
)
def test_validate_influences_invalid_processing_files(
    model_influences, model_class, custom_influences, processing_files
):
    with pytest.raises(CustomInfluencesError) as excinfo:
        validate_influences(
            model_influences, model_class, custom_influences, processing_files
        )
    assert (
        "When multiple processing files are used, influences cannot be anchors."
        == excinfo.value.message
    )


@pytest.mark.parametrize(
    "enabled, drift_dict, classification, drift_type",
    [
        (False, {"age": {"values": [9, 10], "range": True}}, True, "feature"),
        (False, {"age": {"values": [9, 10], "range": True}}, True, "model"),
        (None, {"age": {"values": [9, 10], "range": True}}, True, "feature"),
        (None, {"age": {"values": [9, 10], "range": True}}, True, "model"),
    ],
)
def test_validate_validate_drift_metrics_invalid(
    enabled, drift_dict, classification, drift_type
):
    with pytest.raises(MetricsError) as excinfo:
        validate_drift_metrics(enabled, drift_dict, classification, drift_type)
    assert (
        f"If {drift_type} drift is not enabled, dict must be empty"
        == excinfo.value.message
    )


def test_validate_validate_drift_metrics_invalid_regression():
    with pytest.raises(MetricsError) as excinfo:
        validate_drift_metrics(
            True, {"age": {"values": [9, 10], "range": True}}, False, "model"
        )
    assert (
        "If classification is false, then model drift dict must only"
        " contain a single key/value pair with the key name of 'regression'"
        == excinfo.value.message
    )
    with pytest.raises(MetricsError) as excinfo:
        validate_drift_metrics(
            True,
            {
                "regression": {"values": [9, 10], "range": True},
                "age": {"values": [9, 10], "range": True},
            },
            False,
            "model",
        )
    assert (
        "If classification is false, then model drift dict must only"
        " contain a single key/value pair with the key name of 'regression'"
        == excinfo.value.message
    )


@pytest.mark.parametrize(
    "enabled, feature_list",
    [(False, ["age"]), (None, ["age"])],
)
def test_validate_validate_bias_metrics_invalid(enabled, feature_list):
    with pytest.raises(MetricsError) as excinfo:
        validate_bias_metrics(enabled, feature_list)
    assert "If bias is not enabled, feature list must be empty" == excinfo.value.message


@pytest.mark.parametrize(
    "enabled, drift_dict, classification, drift_type",
    [
        (True, {"age": {"range": True}}, True, "feature"),
        (True, {"age": {"range": True}}, True, "model"),
        (True, [], True, "feature"),
        (True, [], True, "model"),
    ],
)
def test_validate_validate_drift_metrics_invalid_values(
    enabled, drift_dict, classification, drift_type
):
    with pytest.raises(MetricsError) as excinfo:
        validate_drift_metrics(enabled, drift_dict, classification, drift_type)
    assert f"Invalid format for {drift_type} drift dict" == excinfo.value.message
