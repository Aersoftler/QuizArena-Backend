from bson import json_util
from flask import Blueprint, request

from quiz.Session import Session
from user.User import User

session_app = Blueprint('session_app', __name__)


@session_app.route('/session', methods=['GET'])
def get_session_all():
    return json_util.dumps(Session.get_all_sessions()), 200


@session_app.route('/session/<name>', methods=['GET'])
def get_session(name):
    return json_util.dumps(Session(name).get()), 200


@session_app.route('/session/<name>', methods=['PATCH'])
def patch_session(name):
    try:
        Session(name).add_user(User(request.args['user']), request.form['password'])
    except PermissionError as e:
        return e.args[0], 403
    return 'user successfully added', 200
