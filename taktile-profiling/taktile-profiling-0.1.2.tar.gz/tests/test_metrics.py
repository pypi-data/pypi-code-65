import numpy as np
import pytest
from profiling.metrics import AUC, Accuracy


@pytest.mark.parametrize(
    "pred,y,expected",
    [
        ([0, 1], [0, 1], 1.0),
        ([0, 0], [0, 1], 0.5),
        ([1, 1], [0, 1], 0.5),
        ([0, 0.0, 0], [0, 1, 1], 0.50),
        ([0, 0.5, 0], [0, 1, 1], 0.75),
        ([0, 0.5, 1], [0, 1, 1], 1.0),
    ],
)
def test_auc(pred, y, expected):
    pred = np.array(pred)
    y = np.array(y)
    loss = AUC()
    auc = loss.metric(pred, y)
    assert np.isclose(auc, expected)


def test_auc_error():
    with pytest.raises(ValueError):
        loss = AUC()
        pred = np.array([0, 0])
        y = np.array([1, 1])
        loss.metric(pred, y)


@pytest.mark.parametrize(
    "pred,y,expected",
    [
        ([0, 0.6], [0, 1], 1.0),
        ([0, 0.4], [0, 1], 0.5),
        ([1, 0.6], [0, 1], 0.5),
        ([0, 0.0, 0], [0, 1, 1], 1 / 3),
        ([0, 0.6, 0], [0, 1, 1], 2 / 3),
        ([0, 0.6, 1], [0, 1, 1], 1.0),
    ],
)
def test_accuracy(pred, y, expected):
    pred = np.array(pred)
    y = np.array(y)
    loss = Accuracy()
    auc = loss.metric(pred, y)
    assert np.isclose(auc, expected)
