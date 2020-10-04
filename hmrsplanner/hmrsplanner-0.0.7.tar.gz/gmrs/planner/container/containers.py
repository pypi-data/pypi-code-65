"""Containers module."""

import logging.config
from dependency_injector import containers, providers

from ..estimator import Estimator
from ..operators.sequential import Sequential


class Container(containers.DeclarativeContainer):

    config = providers.Configuration()

    configure_logging = providers.Callable(
        logging.config.fileConfig,
        fname='logging.ini',
    )

    sequential_operator = providers.Factory(
        Sequential
    )

    estimator_operator = providers.Factory(
        Estimator
    )


