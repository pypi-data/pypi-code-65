import pathlib
import pandas as pd
import disaster_messaging_classification_model

pd.options.display.max_rows = 100
pd.options.display.max_columns = 50

PACKAGE_ROOT = (
    pathlib.Path(disaster_messaging_classification_model.__file__).resolve().parent
)

MODEL_NAME = "adaboost"
MODEL_SAVE_FILE = f"{MODEL_NAME}_model_v"

TRAINED_MODEL_DIR = PACKAGE_ROOT / "trained_models"
PERFORMACE_REPORT_DIR = "performance_report"
DATASET_DIR = PACKAGE_ROOT / "data"
DATA_FILE_NAME = "disaster_messages.csv"
DATA_CAT_FILE_NAME = "disaster_categories.csv"
DATABASE_NAME = "DisasterResponse.db"
TABLE_NAME = "disaster_messages"

EXTRA_FEATURES_DROP_Y = ["id", "message", "original", "genre", "set_label"]
MESSAGE_FEATURE = "message"

N_ESTIMATORS = 50
PARAMS = {"n_estimators": N_ESTIMATORS}
RANDOM_SEED = 7

CV_FOLDS = 5
N_JOBS = 10


TRAINING_DATA_PCT = 0.85

CLASSES = [
    "related",
    "request",
    "offer",
    "aid_related",
    "medical_help",
    "medical_products",
    "search_and_rescue",
    "security",
    "military",
    "child_alone",
    "water",
    "food",
    "shelter",
    "clothing",
    "money",
    "missing_people",
    "refugees",
    "death",
    "other_aid",
    "infrastructure_related",
    "transport",
    "buildings",
    "electricity",
    "tools",
    "hospitals",
    "shops",
    "aid_centers",
    "other_infrastructure",
    "weather_related",
    "floods",
    "storm",
    "fire",
    "earthquake",
    "cold",
    "other_weather",
    "direct_report",
]

MAX_WORDS = 250
MAX_FONT = 100
