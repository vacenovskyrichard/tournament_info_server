import json
from flask import Flask, jsonify, request, abort, session, Response
import os
import math
from flask import Flask, render_template, request, url_for, redirect
from Tournaments import TournamentManagement, TournamentInfo
from flask_marshmallow import Marshmallow
from flask_cors import CORS
from datetime import date, datetime
from datetime import datetime, timedelta, timezone
from flask_bcrypt import Bcrypt
from flask_mail import Mail, Message
from models import db, Tournament, User, Player,SignedTeam,get_uuid
from config import ApplicationConfig
from apscheduler.schedulers.background import BackgroundScheduler
from ics import Calendar, Event
from flask_migrate import Migrate
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
migrate = Migrate(app, db)

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
            "last_update",
            "user_id",
            "registration_enabled"
        )

tournament_schema = TournamentSchema()
tournaments_schema = TournamentSchema(many=True)
scheduler = BackgroundScheduler()

jwt = JWTManager(app)

@app.after_request
def refresh_expiring_jwts(response):
    response.headers['new_access_token'] = "None"
    response.headers['Access-Control-Expose-Headers'] = '*, Authorization, new_access_token'
    try:
        exp_timestamp = get_jwt()["exp"]
        now = datetime.now(timezone.utc)
        target_timestamp = datetime.timestamp(now + timedelta(minutes=15))
        minutes = str(math.floor((exp_timestamp - target_timestamp)/60))
        seconds = str(round(math.floor((exp_timestamp - target_timestamp)%60)))
        print(f"Time to new access token generation: {minutes} min {seconds} sec.")
        if target_timestamp > exp_timestamp:
            access_token = create_access_token(identity=get_jwt_identity())
            response.headers['new_access_token'] = access_token
        return response
    except (RuntimeError, KeyError):
        # Case where there is not a valid JWT. Just return the original response
        return response


@app.route("/login", methods=["POST"])
def login():
    email = request.json.get("email", None)
    password = request.json.get("password", None)
    isPlayer = request.json.get("isPlayer", None)
    
    if isPlayer:
        user = Player.query.filter_by(email=email).first()
    else:
        user = User.query.filter_by(email=email).first()

    if user is None:
        return jsonify({"error": "Unauthorized"}), 401

    if not bcrypt.check_password_hash(user.password, password):
        return jsonify({"error": "Unauthorized"}), 401

    response = jsonify({"msg": "login successful"})
    access_token = create_access_token(identity=user.id)
    
    response = {"access_token": access_token}
    return jsonify(response), 200

@app.route("/reset", methods=["POST"])
def reset_password():
    email = request.json.get("email", None)
    isPlayer = request.json.get("isPlayer", None)
    subject = 'Reset hesla'
    sender = 'jdem.hrat@email.cz'
    tmp_password = get_uuid()[-10:]
    
    
    if isPlayer:
        user = Player.query.filter_by(email=email).first()
    else:
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
    name = request.json.get("name", None)
    surname = request.json.get("surname", None)
    isPlayer = request.json.get("isPlayer", None)


    if isPlayer:
        user_exists = Player.query.filter_by(email=email).first() is not None
    else:
        user_exists = User.query.filter_by(email=email).first() is not None
        
    if user_exists:
        return jsonify({"error": "User already exists"}), 409
    hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
    
    if isPlayer:
        new_user = Player(email=email, password=hashed_password,name=name,surname=surname)
    else:
        new_user = User(email=email, password=hashed_password,name=name,surname=surname)
        
    db.session.add(new_user)
    db.session.commit()

    return email, 200

@app.route("/google_login", methods=["POST"])
def google_login():
    email = request.json.get("email", None)
    password = request.json.get("password", None)
    name = request.json.get("name", None)
    surname = request.json.get("surname", None)
    isPlayer = request.json.get("isPlayer", None)

    print("isPlayer")
    print(isPlayer)
    print(type(isPlayer))
    

    if isPlayer:

        user_exists = Player.query.filter_by(email=email).first() is not None
    else:
        user_exists = User.query.filter_by(email=email).first() is not None

    if user_exists:
        
        if isPlayer:
            user = Player.query.filter_by(email=email).first()
        else:
            user = User.query.filter_by(email=email).first()
        

        if not bcrypt.check_password_hash(user.password, password):
            return jsonify({"error": "Unauthorized"}), 401

        access_token = create_access_token(identity=user.id)
        response = {"access_token": access_token}
        return jsonify(response), 200    

    hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
        
    if isPlayer:
        new_user = Player(email=email, password=hashed_password,name=name,surname=surname)
    else:
        new_user = User(email=email, password=hashed_password,name=name,surname=surname)
        
    
    db.session.add(new_user)
    db.session.commit()
    
    access_token = create_access_token(identity=new_user.id)
    response = {"access_token": access_token}
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
        .first()
    )
    
    if found_tournament:
        # Update the capacity and signed fields if the tournament is found
        found_tournament.capacity = tournament.capacity
        found_tournament.signed = tournament.signed
        found_tournament.price = tournament.price
        found_tournament.level = tournament.level
    else:
        db.session.add(tournament)
    db.session.commit()
    
@app.route("/get", methods=["GET"])
def get_all_tournaments():
    all_tournaments = Tournament.query.all()
    results = tournaments_schema.dump(all_tournaments)
    sorted_data = sorted(results, key=lambda x: x['date'])
    return jsonify(sorted_data)

@app.route("/get/<id>/", methods=["GET"])
def get_tournament_by_id(id):
    tournament = Tournament.query.get(id)
    return tournament_schema.jsonify(tournament)

@app.route("/post", methods=["POST"])
# @jwt_required()
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
        last_update=datetime.now(),
        user_id=new_tournament["user_id"],
        registration_enabled=new_tournament["registration_enabled"]
    )
    add_to_database(result)
    return tournament_schema.jsonify(result), 200

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
    tournament_to_update.last_update=datetime.now()
    db.session.commit()

    return tournament_schema.jsonify(tournament_to_update)

@app.route("/delete/<id>/", methods=["DELETE"])
@jwt_required()
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
                user_id='1',
                registration_enabled=False
            )
        )
    all_tournaments = Tournament.query.all()
    results = tournaments_schema.dump(all_tournaments)
    return jsonify(results)

@app.route("/filter", methods=["POST"])
def filter_results():
    filters = request.get_json()
    filter_conditions = []
    
    for key in filters:
        filter_subconditions = []
        if filters[key]:
            for values in filters[key]:
                print(getattr(Tournament, key), values["label"])
                filter_subconditions.append((getattr(Tournament, key) == values["label"]))
            filter_conditions.append(db.or_(*filter_subconditions))

    if filter_conditions:
        final_filter = db.and_( *filter_conditions)
    else:
        final_filter = db.and_(True, *filter_conditions)
        
    results = db.session.query(Tournament).filter(final_filter).all()
    if not results:
        return "", 404

    final_results = tournaments_schema.dump(results)
    return jsonify(final_results)

@app.route("/user_info", methods=["POST"])
@jwt_required()
def get_user_info():
    user_id = request.json.get("user_id", None)
    isPlayer = request.json.get("isPlayer", None)
    
    if isPlayer:
        user = Player.query.filter_by(id=user_id).first()
        response = {"id":user.id,"name":user.name,"surname":user.surname,"email":user.email,"role": "player"}
    else:
        user = User.query.filter_by(id=user_id).first()
        response = {"id":user.id,"name":user.name,"surname":user.surname,"email":user.email,"role":user.role}
    if not user:
        return jsonify({"error": "User not found."}), 404
    print("response")
    print(response)
    return jsonify(response), 200

@app.route('/ical.feed/<city>/<areal>/<category>/<level>/', methods=["GET"])
def calendar_feed(city,areal,category,level):
    filter_conditions = []
    if city != "none":
        filter_subconditions = []
        for c in city.split(";"):
            filter_subconditions.append((getattr(Tournament, "city") == c))
        filter_conditions.append(db.or_(*filter_subconditions))
    if areal != "none":
        filter_subconditions = []
        for a in areal.split(";"):
            filter_subconditions.append((getattr(Tournament, "areal") == a))
        filter_conditions.append(db.or_(*filter_subconditions))
    if category != "none":
        filter_subconditions = []
        for c in category.split(";"):
            print("c")
            print(c)
            filter_subconditions.append((getattr(Tournament, "category") == c))
        filter_conditions.append(db.or_(*filter_subconditions))
    if level != "none":
        filter_subconditions = []
        for l in level.split(";"):
            filter_subconditions.append((getattr(Tournament, "level") == l))
        filter_conditions.append(db.or_(*filter_subconditions))

    final_filter = db.and_(*filter_conditions)

    results = db.session.query(Tournament).filter(final_filter).all()
    if not results:
        return "", 404

    c = Calendar()
    
    for res in results:
        start_str = str(res.date) + "-" + res.start
        date_format = "%Y-%m-%d-%H:%M"
        tournament_duration = timedelta(hours=8) if int(res.start.split(":")[0]) < 11 else timedelta(hours=4)
        
        start_time = datetime.strptime(start_str, date_format) - timedelta(hours=2)
        event = Event()
        event.name = res.name
        event.begin = start_time
        event.duration = tournament_duration
        event.description = f"Kategorie: {res.category}\nCena:{res.price}\nPřihlášení: {res.signed}/{res.capacity}\nOrganizátor: {res.organizer}\n"
        event.location = res.city + " " + res.areal    
        event.url = res.link    
        # Add the event to the calendar
        c.events.add(event)    
    
    # Generate the ICS feed
    # ics_feed = c.serialize()
    # return Response(ics_feed, content_type='text/calendar; charset=utf-8')
    
    ics_feed = c.serialize()

    response = Response(ics_feed, content_type='text/calendar; charset=utf-8')
    response.headers['Content-Disposition'] = 'attachment; filename="calendar.ics"'
    return response

@jwt.unauthorized_loader
def unauthorized_callback(e):
    return jsonify({"message": "Token has expired"}), 401

@app.route("/request_organizer", methods=["POST"])
def request_organizer_access():
    user_id = request.json.get("id", None)
    subject = 'Žádost o práva organizátora'
    sender = 'jdem.hrat@email.cz'
    user = User.query.filter_by(id=user_id).first()

    msg = Message(
                subject=subject,
                sender =sender,
                recipients = ["vaceri@seznam.cz"]
               )
    msg.body = f'Uživatel {user.name} {user.surname} žádá o práva organizátora.' 
    mail.send(msg)
    return "", 200


@app.route("/create_team", methods=["POST"])
def create_team():
    player_id = request.json.get("player_id", None)
    
    tournament_id = request.json.get("tournament_id", None)
    teammate_name = request.json.get("teammate_name", None)
    teammate_surname = request.json.get("teammate_surname", None)
    
    new_team = SignedTeam(player_id=player_id,tournament_id=tournament_id,teammate_name=teammate_name,teammate_surname=teammate_surname)
    db.session.add(new_team)
    db.session.commit()

    return jsonify({"message":"Team succesfully signed"}), 200

@app.route("/delete_team", methods=["DELETE"])
def delete_team():
    player_id = request.json.get("player_id", None)
    tournament_id = request.json.get("tournament_id", None)
        
    team_to_delete = SignedTeam.query.filter(SignedTeam.player_id == player_id,SignedTeam.tournament_id==tournament_id).first()
    print("team_to_delete")
    print(team_to_delete)
    db.session.delete(team_to_delete)
    db.session.commit()

    return jsonify({"message":"Team succesfully deleted"}), 200



if __name__ == "__main__":
    app.run()
#     # tm = TournamentManagement()
#     # tm.run_all_scrapers()
#     # for tour in tm.tournament_list:
#     #     print(tour)
#     #     print()
