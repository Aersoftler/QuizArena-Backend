from pymongo import MongoClient

database = MongoClient('localhost', 27017).quizarena
user_coll = database.user
question_coll = database.question
category_coll = database.category
session_coll = database.session
