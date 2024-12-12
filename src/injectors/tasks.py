from base_module.sevices.rabbit import RabbitService
from config import config
from services.tasks import PictureProcessing

from . import connections


def rabbit() -> RabbitService:
    """."""
    return RabbitService(config.rabbit)


def processing_injector() -> PictureProcessing:
    return PictureProcessing(
        pg_connection=connections.pg.acquire_session(), rabbit=rabbit()
    )
