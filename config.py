import os
from datetime import timedelta


class ApplicationConfig:
    SECRET_KEY = "MY_VERY_STRONG_SECRET_KEY"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = True

    SQLALCHEMY_DATABASE_URI = "postgresql://azohcmaq:HQIK2v2P_qWrq7EJ09tGzrv4FhxPfi2k@trumpet.db.elephantsql.com/azohcmaq"
    JWT_SECRET_KEY = "please-remember-to-change-me"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    
    # configuration of mail
    MAIL_SERVER ='smtp.seznam.cz'
    MAIL_PORT = 465
    MAIL_USERNAME = 'jdem.hrat@email.cz'
    MAIL_PASSWORD = 'vEZ@4dQJXSJmF!r'
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
