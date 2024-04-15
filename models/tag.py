from database import db
from models.commonFields import CommonFields


class Tag(db.Model, CommonFields):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    description = db.Column(db.String(255))

    def __repr__(self):
        return f"<Tag {self.name}>"
