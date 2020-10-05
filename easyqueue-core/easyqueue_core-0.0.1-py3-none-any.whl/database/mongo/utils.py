from pymongo.errors import PyMongoError

from easyqueue.database.mongo.exception_mapper import MongoExceptionMapper


def catch_exception(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args,**kwargs)
        except PyMongoError as exc:
            return MongoExceptionMapper.generate_error_response(exc)

    return wrapper
