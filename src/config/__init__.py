import dataclasses as dc
import os

import yaml

from base_module.models import Model


@dc.dataclass
class PgConfig(Model):
    """."""

    host: str = dc.field(default=os.getenv("PGSQL_HOST"))
    port: int = dc.field(default=int(os.getenv("PGSQL_PORT", 5432)))
    user: str = dc.field(default=os.getenv("PGSQL_USER"))
    password: str = dc.field(default=os.getenv("PGSQL_PASS"))
    database: str = dc.field(default=os.getenv("PGSQL_DB_NAME"))
    max_pool_connections: int = dc.field(default=100)
    debug: bool = dc.field(default=False)
    schema: str = dc.field(default="public")


@dc.dataclass
class ProjectConfig(Model):
    """."""

    pg: PgConfig = dc.field(default_factory=PgConfig)
    storage_dir: str = dc.field(default="/mnt")


config: ProjectConfig = ProjectConfig.load(
    yaml.safe_load(open(os.getenv("YAML_PATH", "config_yaml/config.yaml"))) or {}
)
