import enum


class Common(enum.Enum):

    interval_minute = "minute"
    interval_hourly = "hourly"
    interval_daily = "daily"
    interval_weekly = "weekly"
    interval_monthly = "monthly"

    process_status_0 = "INPROGRESS"
    process_status_1 = "FAILED"
    process_status_2 = "COMPLETED"

    logger_app_name = "ftpsync"
    logger_tag_warn = "WARN"
    logger_tag_info = "INFO"
    logger_tag_error = "ERROR"

