from app import create_app
from flask import Flask
import os
from models import db


app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")

db.init_app(app)
