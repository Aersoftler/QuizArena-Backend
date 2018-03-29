from bson import json_util
from flask import Blueprint
from pymongo import errors

from quiz.Category import Category
from shared.Messages import Messages, Errors

category_app = Blueprint('category_app', __name__)


@category_app.route('/category/<category>', methods=['POST'])
def post_category(category):
    try:
        Category(category).add()
    except errors.DuplicateKeyError:
        return Errors.CATEGORY_ALREADY_EXISTS.value, 400
    return Messages.CATEGORY_ADDED_SUCCESS.value, 200


@category_app.route('/category', methods=['GET'])
def get_category_all():
    return json_util.dumps(category['category'] for category in Category.get_all_categories()), 200
