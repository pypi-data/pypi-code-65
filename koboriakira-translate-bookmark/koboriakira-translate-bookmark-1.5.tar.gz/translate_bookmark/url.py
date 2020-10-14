from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from translate_bookmark import article


@dataclass
class Url:
    url: str
    domain: Domain = field(init=False)

    def __post_init__(self):
        self.domain = _get_domain(self.url)

    def get_article(self):
        if self.domain == Domain.PACKERSCOM:
            return article.get_article_for_packers(url=self.url)
        if self.domain == Domain.PACKERSWIRE:
            return article.get_article_for_packerswire(url=self.url)
        if self.domain == Domain.DEV_TO:
            return article.get_article_for_dev_to(url=self.url)
        if self.domain == Domain.OTHER:
            return article.get_article(url=self.url)


class Domain(Enum):
    PACKERSCOM = 'packers.com'
    PACKERSWIRE = 'packerswire.usatoday.com'
    DEV_TO = 'dev.to'
    OTHER = 'other'

    @classmethod
    def to_enum(cls, value: str) -> Domain:
        for domain in Domain:
            if value == domain.value:
                return domain
        return Domain.OTHER


class DomainError(Exception):
    pass


def _get_domain(url: str) -> Domain:
    domain_str = url.replace(
        'http://',
        '').replace(
        'https://',
        '').split('/')[0]
    domain = Domain.to_enum(value=domain_str)
    if domain != Domain.OTHER:
        return domain
    domain_str = _remove_sub_domain(domain=domain_str)
    return Domain.to_enum(value=domain_str)


def _remove_sub_domain(domain: str) -> str:
    splited_domain = domain.split('.')
    if len(splited_domain) == 2:
        return domain
    return f'{splited_domain[1]}.{splited_domain[2]}'
