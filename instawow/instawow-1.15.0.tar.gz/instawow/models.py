from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any, List, Optional as O, Type

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKeyConstraint,
    MetaData,
    String,
    TypeDecorator,
    and_,
    func,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, object_session, relationship

if TYPE_CHECKING:

    class _ModelBase:
        metadata: MetaData

    TZDateTime_base_class = TypeDecorator[datetime]
else:
    TZDateTime_base_class = TypeDecorator


class TZDateTime(TZDateTime_base_class):
    impl = DateTime

    def process_bind_param(self, value: O[datetime], dialect: Any) -> O[datetime]:  # type: ignore
        if value is not None:
            if not value.tzinfo:
                raise TypeError('tzinfo is required')
            value = value.astimezone(timezone.utc).replace(tzinfo=None)
        return value

    def process_result_value(self, value: O[datetime], dialect: Any) -> O[datetime]:
        if value is not None:
            value = value.replace(tzinfo=timezone.utc)
        return value

    @property
    def python_type(self):
        return datetime


ModelBase: Type[_ModelBase] = declarative_base()


class Pkg(ModelBase):
    __tablename__ = 'pkg'

    source = Column(String, primary_key=True)
    id = Column(String, primary_key=True)
    slug = Column(String, nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    url = Column(String, nullable=False)
    download_url = Column(String, nullable=False)
    date_published = Column(TZDateTime, nullable=False)
    version = Column(String, nullable=False)
    folders: relationship[List[PkgFolder]] = relationship(
        'PkgFolder', cascade='all, delete-orphan', backref='pkg'
    )
    options: relationship[PkgOptions] = relationship(
        'PkgOptions', cascade='all, delete-orphan', uselist=False
    )
    deps: relationship[List[PkgDep]] = relationship(
        'PkgDep', cascade='all, delete-orphan', backref='pkg'
    )

    if TYPE_CHECKING:

        def __init__(
            self,
            *,
            source: str,
            id: str,
            slug: str,
            name: str,
            description: str,
            url: str,
            download_url: str,
            date_published: datetime,
            version: str,
            folders: List[PkgFolder] = [],
            options: PkgOptions,
            deps: List[PkgDep] = [],
        ) -> None:
            ...

    @property
    def logged_versions(self) -> List[PkgVersionLog]:
        session: O[Session] = object_session(self)
        return (
            (
                session.query(PkgVersionLog)
                .filter(
                    and_(PkgVersionLog.pkg_source == self.source, PkgVersionLog.pkg_id == self.id)
                )
                .order_by(PkgVersionLog.install_time.desc())
                .all()
            )
            if session
            else []
        )


class PkgFolder(ModelBase):
    __tablename__ = 'pkg_folder'
    __table_args__ = (ForeignKeyConstraint(['pkg_source', 'pkg_id'], ['pkg.source', 'pkg.id']),)

    name = Column(String, primary_key=True)
    pkg_source = Column(String, nullable=False)
    pkg_id = Column(String, nullable=False)

    if TYPE_CHECKING:

        def __init__(self, *, name: str) -> None:
            ...


class PkgOptions(ModelBase):
    __tablename__ = 'pkg_options'
    __table_args__ = (ForeignKeyConstraint(['pkg_source', 'pkg_id'], ['pkg.source', 'pkg.id']),)

    strategy = Column(String, nullable=False)
    pkg_source = Column(String, primary_key=True)
    pkg_id = Column(String, primary_key=True)

    if TYPE_CHECKING:

        def __init__(self, *, strategy: str) -> None:
            ...


class PkgDep(ModelBase):
    __tablename__ = 'pkg_dep'
    __table_args__ = (ForeignKeyConstraint(['pkg_source', 'pkg_id'], ['pkg.source', 'pkg.id']),)

    id = Column(String, primary_key=True)
    pkg_source = Column(String, primary_key=True)
    pkg_id = Column(String, primary_key=True)

    if TYPE_CHECKING:

        def __init__(self, *, id: str) -> None:
            ...


class PkgVersionLog(ModelBase):
    __tablename__ = 'pkg_version_log'

    version = Column(String, primary_key=True)
    install_time = Column(TZDateTime, nullable=False, server_default=func.now())
    pkg_source = Column(String, primary_key=True)
    pkg_id = Column(String, primary_key=True)

    if TYPE_CHECKING:

        def __init__(
            self,
            *,
            version: str,
            pkg_source: str,
            pkg_id: str,
        ) -> None:
            ...


def is_pkg(value: Any) -> bool:
    return isinstance(value, Pkg)
