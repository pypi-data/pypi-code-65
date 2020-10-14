from enum import Enum
from pydantic import BaseModel
from typing import Any, Optional


class Subject(str):
    pass


class ReplyStatus(int, Enum):
    """ReplyStatus can be evaluated as a boolean. It can this be used in if/else statements.
    
    Examples:

        >>> ReplyStatus.FAILURE == True
        False
        
        >>> ReplyStatus.SUCCESS == True
        True
    """

    FAILURE = 0
    SUCCESS = 1


class ReplyMessage(BaseModel):
    """ReplyMessages are returned by NATS request/reply services.

    Attributes:
    -----------
        status: An integer, either 1 (faststan.models.ReplyStatus.SUCCESS) or 0 (faststan.models.ReplyStatus.FAILURE), that denotes success of request.
        error: When status is FAILURE, the exception that caused the failure is available as the error attribute.
        result: When status SUCCESS, the reply value is available as result attribute.  
    """

    status: ReplyStatus
    error: Optional[str] = None
    result: Any = None
