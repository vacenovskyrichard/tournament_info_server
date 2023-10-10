import json
from flask import Flask, jsonify, request, abort, session
import os
from flask import Flask, render_template, request, url_for, redirect
from Tournaments import TournamentManagement, TournamentInfo
from flask_marshmallow import Marshmallow
from flask_cors import CORS
from datetime import date, datetime
from datetime import datetime, timedelta, timezone
from flask_bcrypt import Bcrypt
from flask_mail import Mail, Message
from models import db, Tournament, User, get_uuid
from config import ApplicationConfig
from flask_jwt_extended import (
    create_access_token,
    get_jwt,
    get_jwt_identity,
    unset_jwt_cookies,
    jwt_required,
    verify_jwt_in_request,
    set_access_cookies,
    JWTManager,
)

app = Flask(__name__)
app.config.from_object(ApplicationConfig)
mail = Mail(app) # instantiate the mail class
db.init_app(app=app)

CORS(app)

ma = Marshmallow(app)
bcrypt = Bcrypt(app)

class TournamentSchema(ma.Schema):
    class Meta:
        fields = (
            "id",
            "name",
            "date",
            "city",
            "areal",
            "capacity",
            "signed",
            "price",
            "start",
            "organizer",
            "category",
            "level",
            "link",
            "user_id"
        )

tournament_schema = TournamentSchema()
tournaments_schema = TournamentSchema(many=True)

jwt = JWTManager(app)

@app.after_request
def refresh_expiring_jwts(response):
    try:
        exp_timestamp = get_jwt()["exp"]
        now = datetime.now(timezone.utc)
        target_timestamp = datetime.timestamp(now + timedelta(minutes=30))
        print("============== target time / exp time ===============")
        print(target_timestamp, exp_timestamp)
        if target_timestamp > exp_timestamp:
            access_token = create_access_token(identity=get_jwt_identity())
            print("============== new access token===============")
            print("New access token sent.")
            response.headers['new_access_token'] = access_token

        return response
    except (RuntimeError, KeyError):
        # Case where there is not a valid JWT. Just return the original response
        response.headers['new_access_token'] = None
        return response


@app.route("/login", methods=["POST"])
def login():
    email = request.json.get("email", None)
    password = request.json.get("password", None)
    user = User.query.filter_by(email=email).first()

    if user is None:
        return jsonify({"error": "Unauthorized"}), 401

    if not bcrypt.check_password_hash(user.password, password):
        return jsonify({"error": "Unauthorized"}), 401

    response = jsonify({"msg": "login successful"})
    access_token = create_access_token(identity=user.id)
    
    response = {"access_token": access_token,'role': user.role}
    return jsonify(response), 200

@app.route("/reset", methods=["POST"])
def reset_password():
    email = request.json.get("email", None)
    subject = 'Reset hesla'
    sender = 'jdem.hrat@email.cz'
    print("email")
    print(email)
    print('docasne heslo')
    tmp_password = get_uuid()[-10:]
    print(tmp_password)
    user = User.query.filter_by(email=email).first()

    if user is None:
        return jsonify({"error": "User with this email does not exist"}), 404
    user.password =  bcrypt.generate_password_hash(tmp_password).decode("utf-8")
    db.session.commit()
    
    msg = Message(
                subject=subject,
                sender =sender,
                recipients = [email]
               )
    msg.body = 'Nové heslo je: ' + tmp_password
    mail.send(msg)
    return jsonify({"new_password": tmp_password}), 200

@app.route("/register", methods=["POST"])
def register_user():
    email = request.json.get("email", None)
    password = request.json.get("password", None)

    user_exists = User.query.filter_by(email=email).first() is not None

    if user_exists:
        return jsonify({"error": "User already exists"}), 409
    hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
    new_user = User(email=email, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    return email, 200

@app.route("/google_login", methods=["POST"])
def google_login():
    email = request.json.get("email", None)
    password = request.json.get("password", None)

    print("Google login")
    print(email)
    print(password)
    
    user_exists = User.query.filter_by(email=email).first() is not None

    if user_exists:
        user = User.query.filter_by(email=email).first()

        if not bcrypt.check_password_hash(user.password, password):
            return jsonify({"error": "Unauthorized"}), 401

        access_token = create_access_token(identity=user.id)
        response = {"access_token": access_token,'role': user.role}
        return jsonify(response), 200    

    hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
    new_user = User(email=email, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    user = User.query.filter_by(email=email).first()

    if not bcrypt.check_password_hash(user.password, password):
        return jsonify({"error": "Unauthorized"}), 401

    access_token = create_access_token(identity=email)
    response = {"access_token": access_token,'role': user.role}
    return jsonify(response), 200    

@app.route("/logout", methods=["POST"])
def logout():
    response = jsonify({"msg": "logout successful"})
    unset_jwt_cookies(response)
    return response

def add_to_database(tournament: Tournament):
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
        .all()
    )
    if not found_tournament:
        db.session.add(tournament)
        db.session.commit()
        return True
    return False

@app.route("/get", methods=["GET"])
def get_all_tournaments():
    all_tournaments = Tournament.query.all()
    results = tournaments_schema.dump(all_tournaments)
    return jsonify(results)

@app.route("/get/<id>/", methods=["GET"])
def get_tournament_by_id(id):
    tournament = Tournament.query.get(id)
    return tournament_schema.jsonify(tournament)

@app.route("/post", methods=["POST"])
@jwt_required()
def add_tournament():
    new_tournament = request.get_json()
    result = Tournament(
        name=new_tournament["name"],
        date=new_tournament["date"],
        city=new_tournament["city"],
        areal=new_tournament["areal"],
        capacity=new_tournament["capacity"],
        price=new_tournament["price"],
        start=new_tournament["start"],
        organizer=new_tournament["organizer"],
        category=new_tournament["category"],
        level=new_tournament["level"],
        link=new_tournament["link"],
        user_id=new_tournament["user_id"]
    )
    if add_to_database(result):
        return tournament_schema.jsonify(result), 200
    return {"message": "Tournament already in the database."}, 404

@app.route("/update/<id>/", methods=["PUT"])
def update_tournament(id):
    tournament_to_update = Tournament.query.get(id)

    received_tournament = request.get_json()
    if "name" in received_tournament:
        tournament_to_update.name = received_tournament["name"]

    date_format = "%Y-%m-%d"
    if "date" in received_tournament:
        new_date = received_tournament["date"]
        if isinstance(new_date, str):
            new_date = datetime.strptime(new_date, date_format)
        tournament_to_update.date = new_date
    if "city" in received_tournament:
        tournament_to_update.city = received_tournament["city"]
    if "areal" in received_tournament:
        tournament_to_update.areal = received_tournament["areal"]
    if "capacity" in received_tournament:
        tournament_to_update.capacity = received_tournament["capacity"]
    if "signed" in received_tournament:
        tournament_to_update.signed = received_tournament["signed"]
    if "price" in received_tournament:
        tournament_to_update.price = received_tournament["price"]
    if "start" in received_tournament:
        tournament_to_update.start = received_tournament["start"]
    if "organizer" in received_tournament:
        tournament_to_update.organizer = received_tournament["organizer"]
    if "category" in received_tournament:
        tournament_to_update.category = received_tournament["category"]
    if "level" in received_tournament:
        tournament_to_update.level = received_tournament["level"]
    if "link" in received_tournament:
        tournament_to_update.link = received_tournament["link"]
    db.session.commit()

    return tournament_schema.jsonify(tournament_to_update)

@app.route("/delete/<id>/", methods=["DELETE"])
def delete_tournament_by_id(id):
    tournament = Tournament.query.get(id)
    if tournament:
        db.session.delete(tournament)
        db.session.commit()
        return tournament_schema.jsonify(tournament), 200
    else:
        return "", 404

@app.route("/update", methods=["GET"])
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
    all_tournaments = Tournament.query.all()
    results = tournaments_schema.dump(all_tournaments)
    return jsonify(results)

@app.route("/filter", methods=["POST"])
def filter_results():
    filters = request.get_json()

    filter_conditions = []
    for f in filters:
        if filters[f] == "Bez filtru":
            continue
        filter_conditions.append((getattr(Tournament, f) == filters[f]))

    print(filter_conditions)
    final_filter = db.and_(*filter_conditions)

    results = db.session.query(Tournament).filter(final_filter).all()
    if not results:
        return "", 404

    final_results = tournaments_schema.dump(results)
    return jsonify(final_results)


if __name__ == "__main__":
    app.run(debug=True)
    # tm = TournamentManagement()
    # tm.run_all_scrapers()
    # print(tm.tournament_list)

    