"""Constants - Holds all the default and client configuration"""
import enum


class Config(enum.Enum):
    """Config - Contains client configuration values as an enum"""

    section_client_credential = "client.credential"
    client_credential_user = "user_name"
    client_credential_password = "password"

    section_data_location = "data.location"
    dir_path_list = "dir_path_list"

    section_log_location = "log.location"
    file_process_log = "file_process_log"
    application_log = "application_log"

    section_app_settings = "app.settings"
    compression_type = "compression_type"
    delete_file = "delete_file"


class Constant(enum.Enum):
    """Application configuration as an enum"""

    score_token_url = "http://console.scoredata.com/api/token/"
    score_s3_config_url = "http://console.scoredata.com/dw/logger"

    file_checkpoint_path = "file_checkpoint.log"
    app_log_path = "app.log"
    logger_module_name = "datatransfer"

    default_compression_type = "gz"
    default_s3_limit_mb = 10240

    exit_missing_credential = "Username and password not provided"
    exit_data_path_location = "Dir path missing"


class SavedObj:
    """Holds application and client configuration"""
    config = {}
