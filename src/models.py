import os
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from flask_migrate import Migrate, upgrade
from sqlalchemy import func

app = Flask(__name__)

DB_TYPE = os.getenv('DB_TYPE')
USERNAME = os.getenv('USERNAME')
PSW = os.getenv('PSW')
HOST = os.getenv('HOST')
DB_NAME = os.getenv('DB_NAME')
# Настройка подключения к базе данных PostgreSQL
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{USERNAME}:{PSW}@db/{DB_NAME}'


db = SQLAlchemy(app)
migrate = Migrate(app, db)

with app.app_context():
    upgrade()  # Применяет все миграции


class FileInfo(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    extension = db.Column(db.Text, nullable=True)
    path_file = db.Column(db.Text, nullable=True)
    size = db.Column(db.Float, nullable=True)
    date_create = db.Column(db.DateTime(timezone=True), server_default=func.now(), nullable=False)
    date_change = db.Column(db.DateTime(timezone=True), nullable=True)
    comment = db.Column(db.Text, nullable=True)



if __name__ == '__main__':
    app.run(debug=True)