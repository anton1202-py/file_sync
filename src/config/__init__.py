import dataclasses as dc
import os

import yaml

from base_module.models import Model


@dc.dataclass
class PgConfig(Model):
    """."""

    host: str = dc.field()
    port: int = dc.field()
    user: str = dc.field()
    password: str = dc.field()
    database: str = dc.field()
    max_pool_connections: int = dc.field(default=100)
    debug: bool = dc.field(default=False)
    schema: str = dc.field(default="public")


@dc.dataclass
class OMSPgConfig(PgConfig):
    """."""

    host: str = dc.field(default=os.getenv("STORAGES_PGSQL_HOST"))
    port: int = dc.field(default=int(os.getenv("STORAGES_PGSQL_PORT", 5432)))
    user: str = dc.field(default=os.getenv("STORAGES_PGSQL_USER"))
    password: str = dc.field(default=os.getenv("STORAGES_PGSQL_PASS"))
    database: str = dc.field(default=os.getenv("STORAGES_PGSQL_ORBISMAP_DB"))
    schema: str = dc.field(default="external_modules")


@dc.dataclass
class ProjectConfig(Model):
    """."""

    pg: OMSPgConfig = dc.field(default_factory=OMSPgConfig)
    storage_dir: str = dc.field(default="/mnt")
    host: str = dc.field(default=os.getenv("STORAGES_PGSQL_HOST"))
    port: int = dc.field(default=int(os.getenv("STORAGES_PGSQL_PORT", 5432)))
    user: str = dc.field(default=os.getenv("STORAGES_PGSQL_USER"))
    password: str = dc.field(default=os.getenv("STORAGES_PGSQL_PASS"))
    database: str = dc.field(default=os.getenv("STORAGES_PGSQL_DB"))


config: ProjectConfig = ProjectConfig.load(
    yaml.safe_load(open(os.getenv("YAML_PATH", "config/config.yaml"))) or {}
)
