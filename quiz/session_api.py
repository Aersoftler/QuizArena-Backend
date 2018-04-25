import json
from datetime import datetime, timedelta

from flask import Blueprint, request

from quiz.Session import Session
from shared.JSONEncoder import JSONEncoder
from shared.Messages import Messages, Errors
from user.User import User

session_app = Blueprint('session_app', __name__)


@session_app.route('/session', methods=['GET'])
def get_session_all():
    return JSONEncoder().encode(Session.get_all_sessions()), 200


@session_app.route('/session/by_user/<user>', methods=['GET'])
def get_session_by_user(user):
    return JSONEncoder().encode(Session.get_session_for_user(user)), 200


@session_app.route('/session/<_id>', methods=['GET'])
def get_session(_id):
    session = Session(_id).get()
    return (JSONEncoder().encode(session), 200) if len(session) > 0 else (json.dumps(None), 404)


@session_app.route('/session/<_id>', methods=['PATCH'])
def patch_session(_id):
    user = User(request.form['user'])
    if request.args['update'] == 'add-user':
        try:
            Session(_id).add_user(User(request.form['user']), request.form['password'])
        except PermissionError as e:
            return e.args[0], 403
        except ValueError as e:
            return e.args[0], 400
        return Messages.USER_ADDED_SUCCESS.value, 200
    elif request.args['update'] == 'set-score':
        score = int(request.form['score'])
        try:
            Session(_id).set_users_score(user, score)
            user.add_total_score(score)
        except ValueError as e:
            return e.args[0], 400
        return Messages.SCORE_SET_SUCCESS.value, 200
    elif request.args['update'] == 'close':
        try:
            Session(_id).close_api(user)
        except PermissionError as e:
            return e.args[0], 403
        except ValueError as e:
            return e.args[0], 400
        return 'session successfully closed', 200
    else:
        return Errors.NO_VALID_UPDATE_PARAM.value, 400


@session_app.route('/session/<name>', methods=['POST'])
def post_session(name):
    try:
        session_create_result = Session(name=name,
                                        category=request.form['category'],
                                        private=json.loads(request.form['private']),
                                        password=request.form['password'],
                                        deadline=datetime.now() + timedelta(hours=int(request.form['run-time'])),
                                        admin=request.form['user']).create()
    except ValueError as e:
        return e.args[0], 400
    return str(session_create_result), 200
