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

    def to_answer(self):
        """Возвращает словарь с информацией о файле"""
        return {
            "id": self.id,
            "name": self.name,
            "extension": self.extension,
            "path_file": self.path_file,
            "size": self.size,
            "date_create": self.date_create.isoformat(),
            "date_change": self.date_change.isoformat() if self.date_change else None,
            "comment": self.comment,
        }

if __name__ == '__main__':
    app.run(debug=True)