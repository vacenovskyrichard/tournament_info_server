import os
from datetime import timedelta


# postgres://tournament_info_user:Q0y9BOwD4CBzcWZCPRc0Vv3NLzuDT2gO@dpg-cjmflmnjbvhs73b95di0-a.frankfurt-postgres.render.com/tournament_info
class ApplicationConfig:
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = True

    # SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    SQLALCHEMY_DATABASE_URI = "postgresql://tournament_info_user:Q0y9BOwD4CBzcWZCPRc0Vv3NLzuDT2gO@dpg-cjmflmnjbvhs73b95di0-a.frankfurt-postgres.render.com/tournament_info"

    JWT_SECRET_KEY = "please-remember-to-change-me"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
