from pymongo import MongoClient

connection = MongoClient('ds121309.mlab.com', 21309)
database = connection['quizarena']
database.authenticate('quizarena', 'hier_das_password')
user_coll = database.user
question_coll = database.question
category_coll = database.category
session_coll = database.session
