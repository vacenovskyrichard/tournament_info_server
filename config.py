import os
from datetime import timedelta


class ApplicationConfig:
    SECRET_KEY = "MY_VERY_STRONG_SECRET_KEY"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = True

    SQLALCHEMY_DATABASE_URI = "postgresql://tournament_info_user:Q0y9BOwD4CBzcWZCPRc0Vv3NLzuDT2gO@dpg-cjmflmnjbvhs73b95di0-a.frankfurt-postgres.render.com/tournament_info"
    SQLALCHEMY_BINDS = {
        "user_db": "postgresql://bsrbjxco:B-Xeg9tVWu1GA6YQgqEcCUKYFCYx5dYZ@trumpet.db.elephantsql.com/bsrbjxco"
    }
    JWT_SECRET_KEY = "please-remember-to-change-me"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    
    # configuration of mail
    MAIL_SERVER ='smtp.seznam.cz'
    MAIL_PORT = 465
    MAIL_USERNAME = 'jdem.hrat@email.cz'
    MAIL_PASSWORD = 'vEZ@4dQJXSJmF!r'
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
