from typing import Any, Dict, Optional

import attr


@attr.s(auto_attribs=True)
class BaseErrorContents:
    """  """

    message: Optional[str] = None
    type: Optional[str] = None
    user_message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        message = self.message
        type = self.type
        user_message = self.user_message

        return {
            "message": message,
            "type": type,
            "userMessage": user_message,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "BaseErrorContents":
        message = d.get("message")

        type = d.get("type")

        user_message = d.get("userMessage")

        return BaseErrorContents(
            message=message,
            type=type,
            user_message=user_message,
        )
