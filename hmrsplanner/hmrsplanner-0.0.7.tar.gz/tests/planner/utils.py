
import pytest


def evaluationIn(config, rate, *assepted_pairs):
    found = False
    for a in assepted_pairs:
        if a[0] == config:
            found = True
            assert a[1] == pytest.approx(rate)
            break
    if not found:
        raise Exception('evaluation with config not expected')
