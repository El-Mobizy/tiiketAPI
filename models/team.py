from database import db
from models.commonFields import CommonFields


class Team(db.Model, CommonFields):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.String(255))
    members = db.relationship('User', backref='team', lazy=True)

    def __repr__(self):
        return f"<Team {self.name}>"

    def __str__(self):
        return f"Team: {self.name}"
