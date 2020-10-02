"""
keras-helper: Helpful Keras Import Wrapper
"""


# pylint: disable=C0415,E0401,W1202,C0103,W0611,W0703,W0621,W0702,R0911

def __install_logging():
    try:
        import coloredlogs
        coloredlogs.install()
    except Exception as _:
        pass


def __get_numpy():
    import logging

    try:
        import numpy
        return numpy
    except ImportError as ie:
        logging.info('No Numoy Found: {}'.format(str(ie)))

    logging.error('No Numpy Found')

    return {}


def __get_keras():
    import os
    import logging

    if 'KERAS_BACKEND' in os.environ:
        try:
            import keras
            return keras
        except ImportError as ie:
            logging.info(
                'Keras Backend {} Not Found: {}'.format(os.environ['KERAS_BACKEND'], str(ie)))
            del os.environ['KERAS_BACKEND']

    try:
        import plaidml
        from plaidml.keras import install_backend
        install_backend()

        import keras
        return keras
    except ImportError as ie:
        logging.info('No PlaidML Keras Found: {}'.format(str(ie)))

    try:
        import mxnet
        os.environ['KERAS_BACKEND'] = 'mxnet'

        import keras
        return keras
    except ImportError as ie:
        if 'KERAS_BACKEND' in os.environ:
            del os.environ['KERAS_BACKEND']
        logging.info('No MXNet Keras Found: {}'.format(str(ie)))

    try:
        import cntk
        os.environ['KERAS_BACKEND'] = 'cntk'

        import keras
        return keras
    except ImportError as ie:
        if 'KERAS_BACKEND' in os.environ:
            del os.environ['KERAS_BACKEND']
        logging.info('No CNTK Keras Found: {}'.format(str(ie)))

    try:
        import theano
        os.environ['KERAS_BACKEND'] = 'theano'

        import keras
        return keras
    except ImportError as ie:
        if 'KERAS_BACKEND' in os.environ:
            del os.environ['KERAS_BACKEND']
        logging.info('No Theano Keras Found: {}'.format(str(ie)))

    try:
        from tensorflow import keras
        return keras
    except ImportError as ie:
        logging.info('No Tensorflow Keras Found: {}'.format(str(ie)))

    logging.error('No Keras Backends Found')

    return {}


def __get_pandas():
    import logging
    import os

    if os.environ.get('USE_PANDAS_ALTERNATIVES'):
        try:
            import modin.pandas as pandas
            return pandas
        except Exception as e:
            logging.error('No Modin Found: {}'.format(str(e)))

        try:
            import ray.dataframe as pandas
            return pandas
        except Exception as e:
            logging.error('No Ray Found: {}'.format(str(e)))

    try:
        import pandas
        return pandas
    except ImportError as ie:
        logging.error('No Pandas Found: {}'.format(str(ie)))

    logging.error('No Pandas Found')

    return {}


def __get_matplotlib():
    import logging

    try:
        import seaborn
        import os
        seaborn.set(style=os.environ.get('SEABORN_STYLE', 'darkgrid'))
    except ImportError as ie:
        logging.error('No Seaborn Found: {}'.format(str(ie)))

    try:
        import matplotlib
        return matplotlib
    except ImportError as ie:
        logging.error('No MatPlotLib Found: {}'.format(str(ie)))

    logging.error('No MatPlotLib Found')

    return {}


def __get_plotly():
    import logging

    try:
        import plotly
        return plotly
    except ImportError as ie:
        logging.error('No Plotly Found: {}'.format(str(ie)))

    logging.error('No Plotly Found')

    return {}


def __get_scikit_learn():
    import logging

    try:
        import sklearn
        return sklearn
    except ImportError as ie:
        logging.error('No SciKit-Learn Found: {}'.format(str(ie)))

    logging.error('No SciKit-Learn Found')
    return {}


__install_logging()
numpy = __get_numpy()
keras = __get_keras()
pandas = __get_pandas()
matplotlib = __get_matplotlib()
plotly = __get_plotly()
sklearn = __get_scikit_learn()
