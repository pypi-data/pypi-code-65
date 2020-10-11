import warnings

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)

import tensorflow as tf


class EstimatorWrapper(object):
    def __init__(self, model_path: str):
        self.estimator = tf.contrib.predictor.from_saved_model(model_path)
        self.model_path = model_path

    def __getstate__(self):
        return self.model_path

    def __setstate__(self, model_path: str):
        self.estimator = tf.contrib.predictor.from_saved_model(model_path)
        self.model_path = model_path
