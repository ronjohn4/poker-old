# from flask import render_template, redirect, url_for, request, current_app, Response
# from flask_login import login_required, current_user

# from app.models import Session, Audit, User, History, load_user, clear_user_activity, clear_game_votes
# from app.main.forms import SessionForm, HistoryForm, AddGameForm
from flask import request, Response
from app import db
from app.models import Session
from datetime import datetime
from app.main import bp
from flask_restful import Resource, Api, reqparse



@bp.route('/game/', methods=["PUT"])
def putgame():
    parser = reqparse.RequestParser()
    parser.add_argument('name',
        type=str,
        required=True,
        help="This field cannot be left blank."
    )
    data = parser.parse_args()

    print(data)

    var = Session(
        name=data['name'],
        start_date=datetime.now(),
        end_date=datetime.now(),
        is_active=True
        )
    db.session.add(var)
    db.session.flush()  # flush() so the id is populated after add
    db.session.commit()

    status_code = Response(status=200)
    data['id'] = var.id

    return status_code, data


@bp.route('/game/<id>', methods=["DELETE"])
def deletegame(id):
    Session.query.filter_by(id=id).delete()
    db.session.commit()

    status_code = Response(status=200)
    
    return status_code