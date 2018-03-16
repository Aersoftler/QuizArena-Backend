import json
from bson import json_util
from datetime import datetime, timedelta
from flask import Blueprint, request

from quiz.Session import Session
from user.User import User

session_app = Blueprint('session_app', __name__)


@session_app.route('/session', methods=['GET'])
def get_session_all():
    return json_util.dumps(Session.get_all_sessions()), 200


@session_app.route('/session/<name>', methods=['GET'])
def get_session(name):
    session = Session(name).get()
    return (json_util.dumps(session), 200) if len(session) > 0 else (json.dumps(None), 404)


@session_app.route('/session/<name>', methods=['PATCH'])
def patch_session(name):
    user = User(request.form['user'])
    if request.args['update'] == 'add-user':
        try:
            Session(name).add_user(User(request.form['user']), request.form['password'])
        except PermissionError as e:
            return e.args[0], 403
        return 'user successfully added', 200
    elif request.args['update'] == 'set-score':
        score = int(request.form['score'])
        try:
            Session(name).set_users_score(user, score)
        except ValueError as e:
            return e.args[0], 400
        # add also to total score
        # try:
        #     user.add_total_score(score)
        # except ValueError as e:
        #     return e.args[0], 400
        return 'score successfully set', 200
    elif request.args['update'] == 'close':
        try:
            Session(name).close_api(user)
        except PermissionError as e:
            return e.args[0], 403
        except ValueError as e:
            return e.args[0], 400
        return 'session successfully closed', 200
    else:
        return 'no valid update-parameter', 400


@session_app.route('/session/<name>', methods=['POST'])
def post_session(name):
    try:
        Session(name,
                category=request.form['category'],
                private=json.loads(request.form['private']),
                password=request.form['password'],
                deadline=datetime.now() + timedelta(hours=int(request.form['run-time']))).create()
    except ValueError as e:
        return e.args[0], 400
    return 'session successfully created', 200
