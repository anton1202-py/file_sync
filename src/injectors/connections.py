from config import config
from injectors.pg import PgConnectionInj
from models import *

pg = PgConnectionInj(
    conf=config.pg, init_statements=["CREATE EXTENSION IF NOT EXISTS postgis;"]
)
