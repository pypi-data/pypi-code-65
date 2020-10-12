import sys, os
import pandas as pd
import numpy as np
import pickle
import logging

# import tokenize_function
from disaster_messaging_classification_model.features.message_tokenizer import Tokenizer

# import sklearn
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.model_selection import train_test_split
from sklearn.multioutput import MultiOutputClassifier
from sklearn.ensemble import AdaBoostClassifier

from disaster_messaging_classification_model.config import config
from disaster_messaging_classification_model.utils.model_utils import (
    load_data_from_db,
    evaluate_model,
    save_pipeline,
)
from disaster_messaging_classification_model import __version__ as _version


def build_model_pipeline():
    """
      build NLP pipeline - count words, tf-idf, multiple output classifier,
      grid search the best parameters
    Args: 
        None
    Returns: 
        cross validated classifier object
    """
    #
    pipeline = Pipeline(
        [
            ("tokenizer", Tokenizer()),
            ("vec", CountVectorizer()),
            ("tfidf", TfidfTransformer()),
            ("clf", MultiOutputClassifier(AdaBoostClassifier(**config.PARAMS))),
        ]
    )
    return pipeline


def train_model():

    _logger = logging.getLogger(__name__)

    model_filepath = config.TRAINED_MODEL_DIR / config.MODEL_SAVE_FILE

    _logger.info("Loading training data from db...")

    # load training data
    X_train, Y_train, category_names = load_data_from_db(set_label="train")

    # build pipeline
    _logger.info("Building model...")
    model = build_model_pipeline()

    # train model (hack to save time on circleci)
    if not os.path.exists(f"{model_filepath}{_version}.pkl"):
        _logger.info("Training model...")
        model.fit(X_train, Y_train)

        # save model pipeline
        _logger.info(f"Saving model...")
        save_pipeline(pipeline_to_persist=model)

        _logger.info("Trained model saved!")

        # evaluate model
        _logger.info("Loading training data from db...")
        X_test, Y_test, category_names = load_data_from_db(set_label="test")

        _logger.info("Evaluating model...")
        evaluate_model(model, X_test, Y_test, category_names)

    else:
        _logger.info(
            f"""Found existing trained model at {model_filepath}{_version}, 
              please refer to the performance report for that model."""
        )


if __name__ == "__main__":
    train_model()
