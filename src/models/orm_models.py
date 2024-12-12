import dataclasses as dc
import typing
from datetime import datetime
from enum import Enum

import sqlalchemy as sa
from sqlalchemy import func

from base_module.models import BaseOrmModel, ValuedEnum

SCHEMA_NAME = "external_modules"


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


BaseOrmModel.REGISTRY.mapped(FileInfo)


class TaskStatus(ValuedEnum):
    """."""

    NEW = "new"
    PROCESSING = "processing"
    ERROR = "error"
    DONE = "done"


@dc.dataclass
class PictureProcessingTask(BaseOrmModel):
    """."""

    __tablename__ = "picture_processing_task"

    task_id: typing.Optional[int] = dc.field(
        default=None, metadata={"sa": sa.Column(sa.Integer, primary_key=True)}
    )
    file_id: int = dc.field(default=None, metadata={"sa": sa.Column(sa.Integer)})
    processed_file_id: int = dc.field(default=0, metadata={"sa": sa.Column(sa.Integer)})
    status: TaskStatus = dc.field(
        default=TaskStatus.NEW,
        metadata={
            "sa": sa.Column(
                sa.Enum(TaskStatus, name="tt_raster_calc_status", schema=SCHEMA_NAME)
            )
        },
    )
    processing_parameters: dict = dc.field(
        default=None, metadata={"sa": sa.Column(sa.JSON)}
    )
    created_at: typing.Optional[datetime] = dc.field(
        default_factory=datetime.now, metadata={"sa": sa.Column(sa.DateTime)}
    )
    updated_at: typing.Optional[datetime] = dc.field(
        default=None, metadata={"sa": sa.Column(sa.DateTime)}
    )

    def to_dict(self):
        return {
            "task_id": self.task_id,
            "file_id": self.file_id,
            "processed_file_id": self.processed_file_id,
            "status": self.status.value,
            "processing_parameters": self.processing_parameters,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


BaseOrmModel.REGISTRY.mapped(PictureProcessingTask)
