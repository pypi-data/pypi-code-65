from dataclasses import dataclass
from typing import Optional


@dataclass
class LoginEvent:
    user_id: str
    username: str
    login_success: bool
    ip_address: str
    failure_reason: Optional[str] = None
    session_id: Optional[str] = None
    additional_metadata: Optional[dict] = None
