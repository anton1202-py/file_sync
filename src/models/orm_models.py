import dataclasses as dc
import typing
from datetime import datetime

import sqlalchemy as sa
from sqlalchemy import func

from base_module.models import BaseOrmModel


@dc.dataclass
class FileInfo(BaseOrmModel):
    """."""

    __tablename__ = "file_info"

    id: typing.Optional[int] = dc.field(
        default=None, metadata={"sa": sa.Column(sa.Integer, primary_key=True)}
    )
    name: str = dc.field(
        default=None, metadata={"sa": sa.Column(sa.String, nullable=False)}
    )
    extension: str = dc.field(default=None, metadata={"sa": sa.Column(sa.String)})
    path_file: str = dc.field(default=None, metadata={"sa": sa.Column(sa.String)})
    size: float = dc.field(default=None, metadata={"sa": sa.Column(sa.Float)})
    date_create: datetime = dc.field(
        default_factory=datetime.utcnow,
        metadata={"sa": sa.Column(sa.DateTime, default=func.now())},
    )
    date_change: typing.Optional[datetime] = dc.field(
        default=None, metadata={"sa": sa.Column(sa.DateTime)}
    )
    comment: str = dc.field(default=None, metadata={"sa": sa.Column(sa.Text)})

    def to_answer(self):
        """Возвращает словарь с информацией о файле"""
        return {
            "id": self.id,
            "name": self.name,
            "extension": self.extension,
            "path_file": self.path_file,
            "size": self.size,
            "date_create": self.date_create.isoformat(),
            "date_change": self.date_change.isoformat() if self.date_change else None,
            "comment": self.comment,
        }


BaseOrmModel.REGISTRY.mapped(FileInfo)
