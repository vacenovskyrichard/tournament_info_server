from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from uuid import uuid4

db = SQLAlchemy()


def get_uuid():
    return uuid4().hex

class Tournament(db.Model):
    __tablename__ = "tournament"
    id = db.Column(db.String(32), primary_key=True, unique=True, default=get_uuid)
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
    last_update = db.Column(db.DateTime)
    registration_enabled = db.Column(db.Boolean, default=False)  # Add the boolean column
    
    # Add a foreign key column that references the 'id' of the 'User' table
    user_id = db.Column(db.String(32), db.ForeignKey('user.id'))

    # Define a relationship to the 'User' table
    creator = db.relationship('User', back_populates='tournaments')
    
     # Define a relationship to the SignedTeam table
    signed_teams = db.relationship('SignedTeam', back_populates='tournament')
    
    def __repr__(self):
        return f"{self.name}\nAreal: {self.areal}\n\n"
    
class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.String(32), primary_key=True, unique=True, default=get_uuid)
    email = db.Column(db.String(345), unique=True)
    password = db.Column(db.Text, nullable=False)
    role = db.Column(db.String(50),default="basic")
    name = db.Column(db.String(345),default="unknown")
    surname = db.Column(db.String(345),default="unknown")
    tournaments = db.relationship('Tournament', back_populates='creator')
    
class Player(db.Model):
    __tablename__ = "player"
    id = db.Column(db.String(32), primary_key=True, unique=True, default=get_uuid)
    email = db.Column(db.String(345), unique=True)
    password = db.Column(db.Text, nullable=False)
    name = db.Column(db.String(345),default="unknown")
    surname = db.Column(db.String(345),default="unknown")
    
     # Define a relationship to the SignedTeam table
    signed_teams = db.relationship('SignedTeam', back_populates='player')

class SignedTeam(db.Model):
    __tablename__ = "signed_team"
    player_id = db.Column(db.String(32), db.ForeignKey('player.id'), primary_key=True)
    tournament_id = db.Column(db.String(32), db.ForeignKey('tournament.id'), primary_key=True)
    teammate_name = db.Column(db.String(345),nullable=False,default="unknown")
    teammate_surname = db.Column(db.String(345),nullable=False,default="unknown")

    # Define the relationships to the Player and Tournament tables
    player = db.relationship('Player', back_populates='signed_teams')
    tournament = db.relationship('Tournament', back_populates='signed_teams')

    def __repr__(self):
        return f"First player ID: {self.player_id}\nTeammate: {self.teammate_name} {self.teammate_surname}\n"