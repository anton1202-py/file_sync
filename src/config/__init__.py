import dataclasses as dc
import os

import yaml

from base_module.models import Model


@dc.dataclass
class ConfigProject(Model):
    """."""

    storage_dir: str = dc.field(default="/mnt")
    username: str = dc.field(default=None)
    psw: str = dc.field(default=None)
    db_name: str = dc.field(default=None)


config: ConfigProject = ConfigProject.load(
    yaml.safe_load(open(os.getenv("YAML_PATH", "config.yaml"))) or {}
)
