import dataclasses as dc
import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy


@dc.dataclass
class ConfigProject:
    """."""

    basedir = os.path.abspath(os.path.dirname("/mnt"))

    def init_app(app):
        username = os.getenv("USERNAME")
        psw = os.getenv("PSW")
        db_name = os.getenv("DB_NAME")
        sqlalchemy_database_url = f"postgresql://{username}:{psw}@db/{db_name}"
        app.config["SQLALCHEMY_DATABASE_URI"] = sqlalchemy_database_url


app = Flask(__name__)
ConfigProject.init_app(app)
db = SQLAlchemy(app)
