import logging


logger = logging.getLogger(__name__)


if __name__ == "__main__":  # pragma: no cover
    raise RuntimeError(
        "Calling `convo.nlu.evaluate` directly is no longer supported. Please use "
        "`convo test` to test a combined Core and NLU model or `convo test nlu` "
        "to test an NLU model."
    )
