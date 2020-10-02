from typing import Any, Callable, Dict, List, Optional, Tuple, TypeVar, Union

from starlette.background import BackgroundTasks
from starlette.requests import Request
from starlette.responses import Response

__all__ = [
    "APIResponse",
    "PredictorArgumentGenerator",
    "PredictorClass",
    "PredictorMethod",
    "PredictorMethodArguments",
    "PredictorResponse",
]

PredictorResponse = Union[str, bytes, Response, Dict, List]
APIResponse = Tuple[PredictorResponse, BackgroundTasks]
PredictorClass = TypeVar("PredictorClass")
PredictorMethod = Callable[[Tuple[Any, ...]], PredictorResponse]
PredictorMethodArguments = Tuple[Union[Dict[str, Any], Response], Optional[BackgroundTasks]]
PredictorArgumentGenerator = Callable[[Request], PredictorMethodArguments]
