from typing import Optional

import pika
import sqlalchemy as sa
from sqlalchemy.orm import Session as PGSession

from base_module import sa_operator
from base_module.exceptions import ModuleException
from base_module.rabbit import TaskIdentMessageModel
from base_module.sevices.rabbit import RabbitService
from models.orm_models import FileInfo, PictureProcessingTask, TaskStatus


class PictureProcessing:

    def __init__(
        self,
        pg_connection: PGSession,
        rabbit: RabbitService,
    ):
        self._pg = pg_connection
        self._rabbit = rabbit

    def check_exists(self, file_id: int) -> Optional[FileInfo]:
        return self._pg.query(FileInfo).filter(FileInfo.id == file_id).first()

    def create_task(
        self, file_id: int, processing_parameters: dict
    ) -> PictureProcessingTask:

        if self.check_exists(file_id):
            task = PictureProcessingTask(
                file_id=file_id,
                processing_parameters=processing_parameters,
            )
        else:
            task = PictureProcessingTask(
                file_id=file_id,
                processing_parameters=processing_parameters,
                status=TaskStatus.ERROR,
            )

        self._pg.add(task)
        self._pg.commit()

        message = TaskIdentMessageModel.lazy_load(TaskIdentMessageModel.T(task.task_id))

        published = self._rabbit.publish(message, properties=pika.BasicProperties())
        if published:
            return task.to_dict()

        with self._pg.begin():
            self._pg.delete(task)

    def get_all(self) -> list[PictureProcessingTask]:
        """."""
        with self._pg.begin():
            q = self._pg.query(PictureProcessingTask)
            q = q.order_by(sa.desc(PictureProcessingTask.created_at))
            return q.all()

    def get(self, task_id: int) -> PictureProcessingTask:
        with self._pg.begin():
            task: PictureProcessingTask = (
                self._pg.query(PictureProcessingTask)
                .filter(
                    sa.and_(
                        sa_operator.eq(PictureProcessingTask.task_id, task_id),
                    )
                )
                .one_or_none()
            )
            if task:
                return task.to_dict()

        raise ModuleException("Задача не найдена", code=404)
