from fastapi import Request

from magicapi import g

from fastapi.responses import JSONResponse

from pydantic import BaseModel


class MagicExceptionModel(BaseModel):
    status_code: int = 452
    message: str
    json_response: dict = {}


class MagicException(Exception):
    def __init__(self, message: str, json_response: dict = None):
        self.status_code: int = 452
        self.message: str = message
        self.json_response: dict = json_response or {}

    def make_model(self) -> MagicExceptionModel:
        return MagicExceptionModel(**self.__dict__)


class BackendException(MagicException):
    pass


class FrontendException(MagicException):
    pass


class FirestoreException(MagicException):
    pass


class TwilioException(MagicException):
    pass


@g.app.exception_handler(MagicException)
def backend_exception_handler(request: Request, exc: MagicException):
    print("EXC", exc.__dict__)
    magic_exception_model = exc.make_model()
    return JSONResponse(
        status_code=magic_exception_model.status_code,
        content=magic_exception_model.dict(),
    )
