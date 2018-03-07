from datetime import datetime, timedelta
from time import sleep
from typing import List

from database.database import session_coll
from quiz.Category import Category
from quiz.Question import Question
from quizarena_utils import hash_password
from user.User import User


class Session:

    def __init__(self, name: str, category: str = 'default', private: bool = False, password: str = None,
                 questions: List[Question] = list(), deadline: datetime = datetime.now() + timedelta(days=1),
                 users: List[str] = list(), closed: bool = False):
        self.name = name
        self.category = category
        self.private = private
        self.password = password
        self.questions = questions
        self.deadline = deadline
        self.users = users
        self.closed = closed
        self.password_hashed = False

    def create(self):
        category = Category(self.category)
        if category.get() is None:
            raise ValueError('no matching category found')
        if type(self.deadline) is not datetime:
            raise TypeError('deadline is not a datetime')
        if len(self.questions) >= 11:
            raise ValueError('To many questions assigned')
        if self.private is True:
            if self.password is None:
                raise ValueError('Cannot create a private session without password ')
            self.__create_password()
        self.questions = category.get_random_questions()
        db_dict = self.__dict__
        del db_dict['password_hashed']
        return session_coll.insert(self.__dict__)

    def remove(self):
        return session_coll.delete_one({'name': self.name})

    def add_user(self, user: User, password: str = ''):
        if user.get() is None:
            raise ValueError('User cannot be found in database')
        self.get_private_settings()
        if self.private and self.password != hash_password(password):
            raise PermissionError('wrong password for private Session')
        return session_coll.update_one({'name': self.name}, {'$push': {'users': {'user': user.id, 'score': 0}}})

    def set_users_score(self, user: User, score: int):
        if user.get() is None:
            raise ValueError('User cannot be found in database')
        return session_coll.update_one(
            {'$and': [{'name': self.name}, {'users.user': user.id}]},
            {'$set': {'users.$.score': score}})

    def remove_user(self, user: User):
        return session_coll.update_one({'name': self.name}, {'$pull': {'users': {'user': user.id}}})

    def __create_password(self):
        if not self.password_hashed:
            self.password = hash_password(self.password)
            self.password_hashed = True

    def get(self):
        pipeline = [
            {
                '$lookup':
                    {
                        'from': 'question',
                        'localField': 'questions',
                        'foreignField': '_id',
                        'as': 'questions'
                    }
            },
            {'$match': {'name': self.name}},
            {'$project': {'_id': 0, 'password': 0}}
        ]
        return list(session_coll.aggregate(pipeline))[0]

    def get_private_settings(self):
        settings = list(session_coll.find({'name': self.name}, {'_id': 0, 'password': 1, 'private': 1}))[0]
        self.password = settings['password']
        self.private = settings['private']
        return settings['password'], settings['private']

    @staticmethod
    def close_finished_sessions():
        while True:
            session_coll.update_many({'deadline': {'$lt': datetime.now()}}, {'$set': {'closed': True}})
            sleep(1)

    @staticmethod
    def get_all_sessions():
        return list(session_coll.find({}, {'_id': 0, 'password': 0, 'questions': 0}))
