import pandas as pd
import joblib
from sklearn.pipeline import Pipeline
from sklearn.metrics import precision_score, recall_score, f1_score

from disaster_messaging_classification_model.config import config
from disaster_messaging_classification_model import __version__ as _version

from sqlalchemy import create_engine
import logging
import typing as t
import os

_logger = logging.getLogger(__name__)


def load_data_from_db(set_label="train"):
    """
        Load data from the sqlite database. 
    Args: 
        database_filepath: the path of the database file
        set_label: indicating whether this data is used for train or test
    Returns: 
        X (DataFrame): messages 
        Y (DataFrame): One-hot encoded categories
        category_names (List)
    """

    # load data from database
    database_filepath = config.DATASET_DIR / config.DATABASE_NAME
    engine = create_engine(f"sqlite:///{database_filepath}")
    df = pd.read_sql_table(config.TABLE_NAME, engine)

    # select appropriate set
    df = df[df["set_label"] == set_label]
    X = df[config.MESSAGE_FEATURE]
    Y = df.drop(config.EXTRA_FEATURES_DROP_Y, axis=1)
    category_names = Y.columns

    return X, Y, category_names


def evaluate_model(model, X_test, Y_test, category_names):
    """
        Evaluate the model performances, in terms of f1-score, precison and recall
    Args: 
        model: the model to be evaluated
        X_test: X_test dataframe
        Y_test: Y_test dataframe
        category_names: category names list defined in load data
    Returns: 
        performances (DataFrame)
    """
    # predict on the X_test
    y_pred = model.predict(X_test)

    # build classification report on every column
    performances = []
    for i in range(len(category_names)):
        performances.append(
            [
                f1_score(Y_test.iloc[:, i].values, y_pred[:, i], average="micro"),
                precision_score(
                    Y_test.iloc[:, i].values, y_pred[:, i], average="micro"
                ),
                recall_score(Y_test.iloc[:, i].values, y_pred[:, i], average="micro"),
            ]
        )
    # build dataframe
    performances = pd.DataFrame(
        performances, columns=["f1 score", "precision", "recall"], index=category_names
    )

    save_file_name = f"{config.MODEL_SAVE_FILE}{_version}_performance.csv"
    save_path = config.TRAINED_MODEL_DIR / config.PERFORMACE_REPORT_DIR / save_file_name

    # create performace report directory if not exist
    if not os.path.exists(config.TRAINED_MODEL_DIR / config.PERFORMACE_REPORT_DIR):
        os.makedirs(config.TRAINED_MODEL_DIR / config.PERFORMACE_REPORT_DIR)

    # save performance report to csv
    performances.to_csv(save_path)
    _logger.info(
        f"Performance report for {config.MODEL_SAVE_FILE}{_version} saved at {save_path}"
    )


def save_pipeline(*, pipeline_to_persist) -> None:
    """
    Persist the pipeline.
    Saves the versioned model, and overwrites any previous
    saved models. This ensures that when the package is
    published, there is only one trained model that can be
    called, and we know exactly how it was built.

    """

    # Prepare versioned save file name
    save_file_name = f"{config.MODEL_SAVE_FILE}{_version}.pkl"
    save_path = config.TRAINED_MODEL_DIR / save_file_name

    if not os.path.exists(config.TRAINED_MODEL_DIR):
        os.makedirs(config.TRAINED_MODEL_DIR)

    remove_old_pipelines(files_to_keep=[save_file_name])
    joblib.dump(pipeline_to_persist, save_path)
    _logger.info(f"saved model: {save_file_name}")


def load_pipeline(*, file_name: str) -> Pipeline:
    """Load a persisted pipeline."""

    file_path = config.TRAINED_MODEL_DIR / file_name
    trained_model = joblib.load(filename=file_path)
    return trained_model


def remove_old_pipelines(*, files_to_keep: t.List[str]) -> None:
    """
    Remove old model pipelines.

    This is to ensure there is a simple one-to-one
    mapping between the package version and the model
    version to be imported and used by other applications.
    However, we do also include the immediate previous
    pipeline version for differential testing purposes.
    """
    do_not_delete = files_to_keep + [config.PERFORMACE_REPORT_DIR, "__init__.py"]
    for model_file in config.TRAINED_MODEL_DIR.iterdir():
        if model_file.name not in do_not_delete:
            model_file.unlink()
