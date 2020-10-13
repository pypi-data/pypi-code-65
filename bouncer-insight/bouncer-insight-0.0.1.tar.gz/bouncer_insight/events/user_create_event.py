from dataclasses import dataclass
from typing import Optional

from bouncer_insight.events import Address


@dataclass
class UserCreateEvent:
    user_id: str
    username: str
    phone_number: Optional[str] = None
    email: Optional[str] = None
    shipping_address: Optional[Address] = None
    billing_address: Optional[Address] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    full_name: Optional[str] = None
    ip_address: Optional[str] = None
    session_id: Optional[str] = None
    additional_metadata: Optional[dict] = None

