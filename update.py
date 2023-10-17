# from Tournaments import TournamentManagement
# from datetime import date, datetime
# from models import db, Tournament
# from flask import Flask

# app = Flask(__name__)

# # Configure your app with the appropriate settings
# app.config.from_object('config.ApplicationConfig')

# # Initialize the SQLAlchemy database
# db.init_app(app)

# def add_to_database(tournament):
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

# if __name__ == "__main__":
#     with app.app_context():
#         update_database()


import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

service = Service(executable_path=os.environ.get("CHROMEDRIVER_PATH"))
chrome_options = webdriver.ChromeOptions()
chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--no-sandbox")
driver = webdriver.Chrome(service=service, options=chrome_options)
driver.get("http://www.python.org")
print(driver.title)