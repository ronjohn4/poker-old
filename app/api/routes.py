from flask import request, Response
from app import db
from app.models import Session, User, History, set_user_last_seen
from datetime import datetime
from app.api import bp, api
from flask_restful import Resource, reqparse, marshal, fields, inputs
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound


class DateFormatter(fields.Raw):
    def format(self, value):
        return value.strftime('%Y-%m-%d %H:%M:%S.%f')


history_fields = {
    "id": fields.Integer,
    "session_id": fields.Integer,
    "a_datetime": DateFormatter,
    "story": fields.String,
    "value": fields.String
}

user_fields = {
    'id': fields.Integer,
    'username': fields.String,
    'vote': fields.String,
    'about_me': fields.String,
    'current_session_id': fields.Integer,
    'email': fields.String,
    'password_hash': fields.String,       
    'last_seen': DateFormatter,
    'token': fields.String,
    'token_expiration': fields.String
}

game_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'start_date': DateFormatter,
    'end_date': DateFormatter,
    'is_active': fields.Boolean,
    'is_voting': fields.Boolean,
    'story': fields.String,
    'owner_id': fields.Integer
}


# -----------------------------------------
class Users(Resource):
    @classmethod
    def get(cls, id):        
        try:
            user_single = User.query.filter_by(id=id).one()
        except MultipleResultsFound:
            return {'msg': f"More than 1 user {id} found"}, 404
        except NoResultFound:
            return {'msg': f"User {id} not found"}, 404        
            
        return marshal(user_single, user_fields), 200


class UserName(Resource):
    @classmethod
    def get(cls, id):
        try:
            user_single = User.query.filter_by(id=id).one()
        except MultipleResultsFound:
            return {'msg': f"More than 1 user {id} found"}, 404
        except NoResultFound:
            return {'msg': f"User {id} not found"}, 404

        return {'username': user_single.username}, 200


class UsersVote(Resource):
    @classmethod
    def put(cls, id):
        parser = reqparse.RequestParser()
        parser.add_argument('game',
            type=str,
            required=True,
            help="Field 'game' must be a valid game id."
        )
        parser.add_argument('vote',
            type=str,
            required=True,
            help="Field 'vote' must be defined, even if blank to clear the last vote."
        )
        data = parser.parse_args()

        try:
            user_single = User.query.filter_by(id=id).one()
        except MultipleResultsFound:
            return {'msg': f"More than 1 user {id} found"}, 404
        except NoResultFound:
            return {'msg': f"User {id} not found"}, 404

        user_single.vote = data['vote']
        user_single.current_session_id = data['game']
        db.session.commit()

        # TODO - trigger other players to update the vote
        return marshal(user_single, user_fields), 200

api.add_resource(Users,'/users/<int:id>') # get
api.add_resource(UserName,'/users/<int:id>/username') # get
api.add_resource(UsersVote,'/users/<int:id>/vote') # put


# -----------------------------------------
class gameToggleVote(Resource):
    @classmethod
    def put(cls, id):
        try:
            game_single = Session.query.filter_by(id=id).one()
        except MultipleResultsFound:
            return {'msg': f"More than 1 game {id} found"}, 404
        except NoResultFound:
            return {'msg': f"Game {id} not found"}, 404

        game_single.is_voting = not game_single.is_voting
        db.session.commit()

        return marshal(game_single, game_fields), 200


# -----------------------------------------
class gameStory(Resource):
    @classmethod
    def put(cls, id):
        parser = reqparse.RequestParser()
        parser.add_argument('story',
            type=str,
            required=True,
            help="Field 'Story' must be a valid game id."
        )
        data = parser.parse_args()

        try:
            game_single = Session.query.filter_by(id=id).one()
        except MultipleResultsFound:
            return {'msg': f"More than 1 game {id} found"}, 404
        except NoResultFound:
            return {'msg': f"Game {id} not found"}, 404

        game_single.story = data['story']
        db.session.commit()

        return marshal(game_single, game_fields), 200

        
class game(Resource):
    @classmethod
    def delete(cls, id):
        Session.query.filter_by(id=id).delete()
        db.session.commit()
        
        return 200

    @classmethod
    def get(cls, id):
        try:
            game_single = Session.query.filter_by(id=id).one()
        except MultipleResultsFound:
            return {'msg': f"More than 1 game {id} found"}, 404
        except NoResultFound:
            return {'msg': f"Game {id} not found"}, 404

        return marshal(game_single, game_fields), 200

    @classmethod
    def put(cls, id):
        parser = reqparse.RequestParser()
        parser.add_argument('name',
            type=str,
            required=True,
            help="This field cannot be left blank."
        )
        parser.add_argument('start_date',
            type=lambda x: datetime.strptime(x,'%Y-%m-%d %H:%M:%S.%f'),
            required=False,
            help="This field cannot be left blank."
        )
        parser.add_argument('end_date',
            type=lambda x: datetime.strptime(x,'%Y-%m-%d %H:%M:%S.%f'),
            required=False,
            help="This field cannot be left blank."
        )
        parser.add_argument('is_active',
            type=bool,
            required=True,
            help="This field cannot be left blank."
        )
        parser.add_argument('is_voting',
            type=bool,
            required=True,
            help="This field cannot be left blank."
        )
        parser.add_argument('story',
            type=str,
            required=True,
            help="This field cannot be left blank."
        )
        parser.add_argument('owner_id',
            type=int,
            required=True,
            help="This field cannot be left blank."
        )
        data = parser.parse_args()

        try:
            game_single = Session.query.filter_by(id=id).one()
        except MultipleResultsFound:
            return {'msg': f"More than 1 game {id} found"}, 404
        except NoResultFound:
            return {'msg': f"Game {id} not found"}, 404

        game_single.name = data['name']
        game_single.start_date = data['start_date']
        game_single.end_date = data['end_date']
        game_single.is_active = data['is_active']
        game_single.is_voting = data['is_voting']
        game_single.story = data['story']
        game_single.owner_id = data['owner_id']
        db.session.commit()

        return marshal(game_single, game_fields), 200


class gameHistory(Resource):
    @classmethod
    def post(cls, id):
        parser = reqparse.RequestParser()
        parser.add_argument('story',
            type=str,
            required=True,
            help="This field cannot be left blank."
        )
        parser.add_argument('value',
            type=str,
            required=True,
            help="This field cannot be left blank."
        )
        data = parser.parse_args()

        var = History(
            session_id=id,
            a_datetime=datetime.now(),
            story=data['story'],
            value=data['value'],
            )    

        db.session.add(var)
        db.session.flush()  # flush() so the id is populated after add
        db.session.commit()

        return marshal(var.to_dict(), history_fields), 200


class games(Resource):
    @classmethod
    def get(cls):
        game_list = Session.query.all()
        return marshal(game_list, game_fields), 200

    @classmethod
    def post(cls):
        parser = reqparse.RequestParser()
        parser.add_argument('name',
            type=str,
            required=True,
            help="This field cannot be left blank."
        )
        parser.add_argument('current_user_id',
            type=int,
            required=True,
            help="This field cannot be left blank."
        )
        data = parser.parse_args()

        var = Session(
            name=data['name'],
            start_date=datetime.now(),
            end_date=None,
            is_active=True, 
            is_voting=False,
            owner_id=data['current_user_id']
            )    

        db.session.add(var)
        db.session.flush()  # flush() so the id is populated after add
        db.session.commit()

        OwnedCount = Session.query.order_by(Session.end_date.asc()).filter_by(owner_id=data['current_user_id']).count()
        MaxAllowed = 20

        if OwnedCount > MaxAllowed:
            oldest_game = Session.query.order_by(Session.start_date.asc()).filter_by(owner_id=data['current_user_id']).first()
            db.session.delete(oldest_game)
            db.session.commit()

        return marshal(var.to_dict(), game_fields), 200


api.add_resource(game,'/games/<int:id>') # delete, get, put
api.add_resource(games,'/games') # post(new) get(list)
api.add_resource(gameToggleVote,'/games/<int:id>/togglevote') # put(specific action)
api.add_resource(gameStory,'/games/<int:id>/story') # put(specific action)
api.add_resource(gameHistory,'/games/<int:id>/history') # post(new)


# -----------------------------------------
# class Login(Resource):
#     @classmethod
#     def post(cls):
#         if current_user.is_authenticated:
#             return {''}
#         form = LoginForm()
#         if form.validate_on_submit():
#             user = User.query.filter_by(username=form.username.data).first()
#             if user is None or not user.check_password(form.password.data):
#                 flash('Invalid username or password')
#                 return redirect(url_for('.login'))
#             login_user(user, remember=form.remember_me.data)
#             next_page = request.args.get('next')
#             if not next_page or url_parse(next_page).netloc != '':
#                 next_page = url_for('main.list')
#             return redirect(next_page)
#         return render_template('auth/login.html', title='Sign In', form=form)

# api.add_resource('Login', '/login') # post
