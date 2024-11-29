import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy


class ConfigProject:
    @staticmethod
    def init_app(app):
        basedir = os.path.abspath(os.path.dirname(__file__))
        USERNAME = os.getenv('USERNAME')
        PSW = os.getenv('PSW')
        DB_NAME = os.getenv('DB_NAME')
        SQLALCHEMY_DATABASE_URI = f'postgresql://{USERNAME}:{PSW}@db/{DB_NAME}'

        app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI


app = Flask(__name__)
ConfigProject.init_app(app)
db = SQLAlchemy(app)