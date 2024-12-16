from config import config
from injectors.tasks import rabbit
from services.services import SyncFileWithDb, WorkerWithFIles
from services.task_worker import TasksWorker

from . import connections


def sync_injector() -> SyncFileWithDb:
    return SyncFileWithDb(
        pg_connection=connections.pg.acquire_session(), storage_dir=config.storage_dir
    )


def file_injector() -> WorkerWithFIles:
    return WorkerWithFIles(
        pg_connection=connections.pg.acquire_session(), storage_dir=config.storage_dir
    )


def tasks_mule() -> TasksWorker:
    """."""
    return TasksWorker(
        rabbit=rabbit(),
        pg_connection=connections.pg.acquire_session(),
        storage_dir=config.storage_dir,
        # oms=file_conf(),
    )
