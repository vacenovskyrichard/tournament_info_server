# from flask import Flask, jsonify
# from flask import Flask
# from Tournaments import TournamentManagement
# from datetime import date, datetime
# from models import db, Tournament
# from config import ApplicationConfig
# from flask_marshmallow import Marshmallow

# app = Flask(__name__)
# app.config.from_object(ApplicationConfig)
# db.init_app(app=app)

# ma = Marshmallow(app)
# class TournamentSchema(ma.Schema):
#     class Meta:
#         fields = (
#             "id",
#             "name",
#             "date",
#             "city",
#             "areal",
#             "capacity",
#             "signed",
#             "price",
#             "start",
#             "organizer",
#             "category",
#             "level",
#             "link",
#             "user_id"
#         )

# tournament_schema = TournamentSchema()
# tournaments_schema = TournamentSchema(many=True)

# def add_to_database(tournament: Tournament):
#     date_format = "%Y-%m-%d"

#     if isinstance(tournament.date, str):
#         tournament.date = datetime.strptime(tournament.date, date_format)

#     found_tournament = (
#         db.session.query(Tournament)
#         .filter(
#             db.and_(
#                 Tournament.name == tournament.name,
#                 Tournament.areal == tournament.areal,
#                 Tournament.date
#                 == date(
#                     tournament.date.year, tournament.date.month, tournament.date.day
#                 ),
#             )
#         )
#         .first()
#     )
    
#     if found_tournament:
#         # Update the capacity and signed fields if the tournament is found
#         found_tournament.capacity = tournament.capacity
#         found_tournament.signed = tournament.signed
#     else:
#         db.session.add(tournament)
#     db.session.commit()

# def update_database():
#     tournaments = TournamentManagement()
#     found_tournaments = tournaments.run_all_scrapers()
#     for tournament in found_tournaments:
#         add_to_database(
#             Tournament(
#                 name=tournament.name,
#                 date=tournament.tournament_date,
#                 city=tournament.city,
#                 areal=tournament.areal,
#                 capacity=tournament.capacity,
#                 signed=tournament.signed,
#                 price=tournament.price,
#                 start=tournament.start,
#                 organizer=tournament.organizer,
#                 category=tournament.category,
#                 level=tournament.level,
#                 link=tournament.link,
#                 user_id='1'
#             )
#         )
#     all_tournaments = Tournament.query.all()
#     results = tournaments_schema.dump(all_tournaments)
#     return jsonify(results)


# if __name__ == "__main__":
#     update_database()

from Tournaments import TournamentManagement
from datetime import date, datetime
from models import db, Tournament
from flask import Flask

app = Flask(__name__)

# Configure your app with the appropriate settings
app.config.from_object('config.ApplicationConfig')

# Initialize the SQLAlchemy database
db.init_app(app)

def add_to_database(tournament):
    date_format = "%Y-%m-%d"

    if isinstance(tournament.date, str):
        tournament.date = datetime.strptime(tournament.date, date_format)

    found_tournament = (
        db.session.query(Tournament)
        .filter(
            db.and_(
                Tournament.name == tournament.name,
                Tournament.areal == tournament.areal,
                Tournament.date
                == date(
                    tournament.date.year, tournament.date.month, tournament.date.day
                ),
            )
        )
        .first()
    )
    
    if found_tournament:
        found_tournament.capacity = tournament.capacity
        found_tournament.signed = tournament.signed
    else:
        db.session.add(tournament)
    db.session.commit()

def update_database():
    tournaments = TournamentManagement()
    found_tournaments = tournaments.run_all_scrapers()
    for tournament in found_tournaments:
        add_to_database(
            Tournament(
                name=tournament.name,
                date=tournament.tournament_date,
                city=tournament.city,
                areal=tournament.areal,
                capacity=tournament.capacity,
                signed=tournament.signed,
                price=tournament.price,
                start=tournament.start,
                organizer=tournament.organizer,
                category=tournament.category,
                level=tournament.level,
                link=tournament.link,
                user_id='1'
            )
        )

if __name__ == "__main__":
    with app.app_context():
        update_database()
