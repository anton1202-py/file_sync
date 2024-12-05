from services.services import SyncFileWithDb, WorkerWithFIles

from . import connections


def sync_injector() -> SyncFileWithDb:
    return SyncFileWithDb(pg_connection=connections.pg.acquire_session())


def file_injector() -> WorkerWithFIles:
    return WorkerWithFIles(pg_connection=connections.pg.acquire_session())
