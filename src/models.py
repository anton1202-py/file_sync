from sqlalchemy import func
from config import db, app

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