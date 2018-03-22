from flask import Blueprint
from pymongo import errors

from quiz.Category import Category

category_app = Blueprint('category_app', __name__)


@category_app.route('/category/<category>', methods=['POST'])
def post_category(category):
    try:
        Category(category).add()
    except errors.DuplicateKeyError as e:
        return e.args[0], 400
    return 'category successfully created', 200
