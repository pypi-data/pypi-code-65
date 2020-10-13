from dataclasses import dataclass
from enum import Enum
from typing import Optional

from bouncer_insight.events import Address


@dataclass
class Card:
    card_type: Optional[str] = None
    card_brand: Optional[str] = None
    card_funding: Optional[str] = None
    card_fingerprint: Optional[str] = None
    card_bin: Optional[str] = None
    card_last4: Optional[str] = None
    card_exp_month: Optional[str] = None
    card_exp_year: Optional[str] = None
    card_name: Optional[str] = None
    card_address: Optional[Address] = None
    card_cvc_check: Optional[str] = None
    card_zip_check: Optional[str] = None


@dataclass
class Paypal:
    paypal_email: Optional[str] = None


class PaymentMethodType(Enum):
    CARD = 'card'
    PAYPAL = 'paypal'


@dataclass
class PaymentMethodAddEvent:
    user_id: str
    payment_method_id: str
    payment_method_type: PaymentMethodType
    payment_gateway: str
    success: bool
    paypal: Optional[Paypal] = None
    card: Optional[Card] = None
    failure_code: Optional[str] = None
    decline_code: Optional[str] = None
    failure_reason: Optional[str] = None
    ip_address: Optional[str] = None
    session_id: Optional[str] = None
    additional_metadata: Optional[dict] = None

    def __post_init__(self):
        self.validate()

    def validate(self):
        if not isinstance(self.payment_method_type, PaymentMethodType):
            raise TypeError("payment_method_type not of expected type PaymentMethodType")

        if self.payment_method_type == PaymentMethodType.CARD and not self.card:
            raise ValueError("payment_method_type set as CARD but no 'card' data found")

        if self.payment_method_type == PaymentMethodType.PAYPAL and not self.paypal:
            raise ValueError("payment_method_type set as PAYPAL but no 'paypal' data found")

        if self.paypal and self.card:
            raise ValueError("Multiple payment method data types found")