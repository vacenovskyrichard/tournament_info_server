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
    """Adds tournament to database if not existing, or updating existing one

    Args:
        tournament (Tournament): tournament to be added or updated
    """
    date_format = "%Y-%m-%d"
    
    #TODO why is this here?
    if isinstance(tournament.date, str):
        tournament.date = datetime.strptime(tournament.date, date_format)
    if isinstance(tournament.last_update, str):
        tournament.last_update = datetime.strptime(tournament.last_update, date_format)

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
        found_tournament.price = tournament.price
        found_tournament.start = tournament.start
        found_tournament.organizer = tournament.organizer
        found_tournament.level = tournament.level
        found_tournament.link = tournament.link
        found_tournament.last_update = tournament.last_update
    else:
        db.session.add(tournament)
    db.session.commit()

def delete_old_tournaments():
    old_tournaments = db.session.query(Tournament).filter(Tournament.date < date.today()).all()
    for t in old_tournaments:
        print("tournament to be deleted: " + str(t))
        db.session.delete(t)
    db.session.commit()

def update_database():
    delete_old_tournaments()
    # init tournament management class
    tm = TournamentManagement()
    # run web scraping
    found_tournaments = tm.run_all_scrapers()
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
                last_update=tournament.last_update,
                user_id='1'
            )
        )

if __name__ == "__main__":
    with app.app_context():
        update_database()