import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

basedir = os.path.abspath(os.path.dirname(__file__))

USERNAME = os.getenv('USERNAME')
PSW = os.getenv('PSW')
DB_NAME = os.getenv('DB_NAME')
SQLALCHEMY_DATABASE_URI = f'postgresql://{USERNAME}:{PSW}@localhost/{DB_NAME}'

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI

db = SQLAlchemy(app)
migrate = Migrate(app, db)