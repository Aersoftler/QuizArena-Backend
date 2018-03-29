import json

from flask import Blueprint, request
from pymongo import errors

from shared.Messages import Errors as err
from shared.Messages import Messages as msg
from user.User import User

user_app = Blueprint('user_app', __name__)


@user_app.route('/user/<user>', methods=['GET'])
def get_user(user):
    user = User(user).get_api()
    return (json.dumps(user), 200) if user is not None else (json.dumps(user), 404)


@user_app.route('/user/<user>', methods=['PATCH'])
def patch_user(user):
    if request.args['update'] == 'password':
        try:
            User(user).update_password_api(request.form['new_password'], request.form['old_password'])
        except ValueError as e:
            return e.args[0], 400
        return msg.PW_CHANGED_SUCCESS.value, 200
    elif request.args['update'] == 'display_name':
        try:
            User(user, display_name=request.form['display_name']).update_display_name()
        except ValueError as e:
            return e.args[0], 400
        return msg.DISPLAY_NAME_CHANGED_SUCCESS.value, 200
    elif request.args['update'] == 'total_score':
        try:
            User(user).add_total_score(int(request.form['score']))
        except ValueError as e:
            return e.args[0], 400
        return msg.SCORE_ADDED_SUCCESS.value, 200
    else:
        return err.NO_VALID_UPDATE_PARAM.value, 400


@user_app.route('/user/<user>', methods=['POST'])
def post_user(user):
    try:
        User(user, password=request.form['password']).register()
    except ValueError as e:
        return e.args[0], 400
    except errors.DuplicateKeyError as e:
        return e.args[0], 400
    return msg.USER_REGISTERED_SUCCESS.value, 200
