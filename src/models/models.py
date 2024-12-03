import dataclasses as dc
import typing

import sqlalchemy as sa
from sqlalchemy import Column, DateTime, Float, Integer, Text, func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class FileInfo(Base):
    __tablename__ = "file_info"  # Указываем имя таблицы

    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)
    extension = Column(Text, nullable=True)
    path_file = Column(Text, nullable=True)
    size = Column(Float, nullable=True)
    date_create = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    date_change = Column(DateTime(timezone=True), nullable=True)
    comment = Column(Text, nullable=True)

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
