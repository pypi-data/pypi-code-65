from __future__ import annotations

from typing import Type, TYPE_CHECKING

if TYPE_CHECKING:
    from guarani.oauth2.grants.base import BaseGrant


class Configuration:
    def __init__(
        self,
        issuer: str,
        grants: list[Type[BaseGrant]],
        scopes: list[str],
        error_url: str,
        token_lifespan: int,
    ):
        self.issuer = issuer
        self.authorization_grants = [
            grant for grant in grants if grant.__response_type__ is not None
        ]
        self.token_grants = [
            grant for grant in grants if grant.__grant_type__ is not None
        ]
        self.scopes = scopes
        self.error_url = error_url
        self.token_lifespan = token_lifespan
