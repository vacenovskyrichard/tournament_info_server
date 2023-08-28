from flask_sqlalchemy import SQLAlchemy
from uuid import uuid4

db = SQLAlchemy()


class Tournament(db.Model):
    __tablename__ = "tournament"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    date = db.Column(db.Date, nullable=False)
    city = db.Column(db.String(100), nullable=False)
    areal = db.Column(db.String(100), nullable=False)
    capacity = db.Column(db.Integer)
    signed = db.Column(db.Integer)
    price = db.Column(db.Integer)
    start = db.Column(db.String(20))
    organizer = db.Column(db.String(100))
    category = db.Column(db.String(100))
    level = db.Column(db.String(100))
    link = db.Column(db.String(100))

    def __repr__(self):
        return f"{self.name}\nAreal: {self.areal}\n\n"
