import dataclasses as dc
import typing as t
from datetime import date, datetime

import dataclass_factory
from sqlalchemy.ext.declarative import declarative_base

TV_MODEL = t.TypeVar("TV_MODEL")

Base = declarative_base()


def default_loader(value, cls, loader):
    if not isinstance(value, cls):
        return loader(value)
    return value


def iso_loader(value: str, cls):
    if isinstance(value, cls):
        return value
    if value.endswith("Z"):
        return cls.fromisoformat(value.replace("Z", ""))
    return cls.fromisoformat(value)


@dc.dataclass
class Model:
    """."""

    SCHEMAS: t.ClassVar = {
        datetime: dataclass_factory.Schema[datetime](
            parser=lambda _: iso_loader(_, datetime), serializer=datetime.isoformat
        ),
        date: dataclass_factory.Schema(
            parser=lambda _: default_loader(_, date, date.fromisoformat),
            serializer=date.isoformat,
        ),
    }
    FACTORY: t.ClassVar = dataclass_factory.Factory(schemas=SCHEMAS)

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.FACTORY = dataclass_factory.Factory(schemas=cls.SCHEMAS)

    @classmethod
    def __improve_schemas(cls):
        for key, schema in cls.SCHEMAS.items():
            cls.FACTORY.schemas.setdefault(key, schema)

    @classmethod
    def load(cls: t.Type[TV_MODEL], data: dict) -> TV_MODEL:
        cls.__improve_schemas()
        if isinstance(data, cls):
            return data
        return cls.FACTORY.load(data, cls)
