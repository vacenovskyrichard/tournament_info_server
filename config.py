import os

basedir = os.path.abspath(os.path.dirname(__file__))

# postgres://tournament_info_user:Q0y9BOwD4CBzcWZCPRc0Vv3NLzuDT2gO@dpg-cjmflmnjbvhs73b95di0-a.frankfurt-postgres.render.com/tournament_info


class ApplicationConfig:
    SECRET_KEY = os.environ["SECRET_KEY"]
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = True

    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    # SQLALCHEMY_BINDS = {"user_db": "sqlite:///" + os.path.join(basedir, "users.db")}
