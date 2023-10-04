from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
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
    # Add a foreign key column that references the 'id' of the 'User' table
    user_id = db.Column(db.String(32), db.ForeignKey('user.id'))

    # Define a relationship to the 'User' table
    creator = db.relationship('User', back_populates='tournaments')
    def __repr__(self):
        return f"{self.name}\nAreal: {self.areal}\n\n"


def get_uuid():
    return uuid4().hex
    
class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.String(32), primary_key=True, unique=True, default=get_uuid)
    email = db.Column(db.String(345), unique=True)
    password = db.Column(db.Text, nullable=False)
    role = db.Column(db.String(50),default="basic")
    name = db.Column(db.String(345),default="unknown")
    surname = db.Column(db.String(345),default="unknown")
    tournaments = db.relationship('Tournament', back_populates='creator')
