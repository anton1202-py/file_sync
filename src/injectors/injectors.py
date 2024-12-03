from services.services import SyncFileWithDb, WorkerWithFIles


def sync_injector() -> SyncFileWithDb:
    from app import session

    return SyncFileWithDb(session)


def file_injector() -> WorkerWithFIles:
    from app import session

    return WorkerWithFIles(session)
