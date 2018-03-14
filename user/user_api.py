import json
from flask import Blueprint, request
from pymongo import errors

from user.User import User

user_app = Blueprint('user_app', __name__)


@user_app.route('/user/<user>', methods=['GET'])
def get_user(user):
    user = User(user).get_api()
    return json.dumps(user), 200 if user is not None else json.dumps(user), 404


@user_app.route('/user/<user>', methods=['PATCH'])
def patch_user(user):
    if request.args['update'] == 'password':
        try:
            User(user, password=request.form['new_password'])\
                .update_password_api(request.form['old_password'])
        except ValueError as e:
            return e.args[0], 400
        return 'Password successfully changed', 200
    elif request.args['update'] == 'display_name':
        try:
            User(user, display_name=request.form['display_name']).update_display_name()
        except ValueError as e:
            return e.args[0], 400
        return 'display_name successfully changed', 200
    elif request.args['update'] == 'total_score':
        try:
            User(user).add_total_score(int(request.form['score']))
        except ValueError as e:
            return e.args[0], 400
        return 'score successfully added to total-score', 200
    else:
        return 'no valid update-parameter', 400


@user_app.route('/user/<user>', methods=['POST'])
def post_user(user):
    try:
        User(user, password=request.form['password']).register()
    except ValueError as e:
        return e.args[0], 400
    except errors.DuplicateKeyError as e:
        return e.args[0], 400
    return 'user successfully registered', 200
