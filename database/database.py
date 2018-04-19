from pymongo import MongoClient

from shared.read_credentials import mongo_creds

connection = MongoClient('ds121309.mlab.com', 21309)
database = connection['quizarena']
database.authenticate(mongo_creds[0], mongo_creds[1])
user_coll = database.user
question_coll = database.question
category_coll = database.category
session_coll = database.session
