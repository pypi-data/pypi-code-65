import os

# engine control
ENV_ENGINE = "MINION_ENGINE"
ENV_DRY_MODE = "DRY"
ENGINE_GOOGLE = "google"
ENGINE_EXECO = "execo"
ENGINE_PULSAR = "pulsar"

# default to some engine
ENGINE = os.getenv(ENV_ENGINE, ENGINE_EXECO)

# reporter control
ENV_REPORTER = "MINION_REPORTER"
REPORTER_STDOUT = "stdout"
REPORTER_NULL = "null"
REPORTER_JSON = "json"

# default to some reporter
REPORTER = os.getenv(ENV_REPORTER, REPORTER_NULL)

# json reporter
ENV_REPORTER_JSON_DIRECTORY = "REPORTER_JSON_DIRECTORY"
DEFAULT_JSON_REPORTER_DIRECTORY = "minion-report"
