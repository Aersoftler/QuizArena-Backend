from datetime import datetime, timedelta
from time import sleep
from typing import List

from database.database import session_coll
from quiz.Category import Category
from quiz.Question import Question
from quizarena_utils import hash_password
from user.User import User
from shared.Messages import Errors as err


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
            raise ValueError(err.NO_MATCHING_CATEGORY)
        if type(self.deadline) is not datetime:
            raise TypeError(err.TYPE_MISMATCH)
        if len(self.questions) >= 11:
            raise ValueError(err.TOO_MANY_QUESTIONS)
        if self.private is True:
            if self.password is None:
                raise ValueError(err.NO_PW_FOR_PRIVATE_SESSION)
            self.__create_password()
        self.questions = category.get_random_questions()
        db_dict = self.__dict__
        del db_dict['password_hashed']
        return session_coll.insert(self.__dict__)

    def remove(self):
        return session_coll.delete_one({'name': self.name})

    def add_user(self, user: User, password: str = ''):
        if not user.exists():
            raise ValueError(err.USER_NOT_FOUND)
        self.get_private_settings()
        if self.private and self.password != hash_password(password):
            raise PermissionError(err.PW)
        self.get_users()
        return session_coll.update_one(
            {'name': self.name},
        )
            {'$push': {'users': {'user': user.id, 'score': 0, 'admin': len(self.users) < 1}}}

    def set_users_score(self, user: User, score: int):
        if user.get() is None:
            raise ValueError(err.USER_NOT_FOUND)
        return session_coll.update_one(
            {'$and': [{'name': self.name}, {'users.user': user.id}]},
            {'$set': {'users.$.score': score}}
        )

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
        return list(session_coll.aggregate(pipeline))

    def get_private_settings(self):
        settings = list(session_coll.find({'name': self.name}, {'_id': 0, 'password': 1, 'private': 1}))[0]
        self.password = settings['password']
        self.private = settings['private']
        return settings['password'], settings['private']

    def get_users(self):
        session = list(session_coll.find({'name': self.name}, {'_id': 0, 'users': 1}))[0]['users']
        self.users = session
        return session

    def close_api(self, user: User):
        if not user.exists():
            raise ValueError('user does not exist')
        is_admin = list(session_coll.find(
            {'name': self.name},
            {'_id': 0, 'users': {'$elemMatch': {'user': user.id}}}))[0]['users'][0]['admin']
        if not is_admin:
            raise PermissionError('user not permitted to close_api session')
        self.close()
        return user

    def close(self):
        session_coll.update_one({'name': self.name}, {'$set': {'closed': True}})

    @staticmethod
    def tidy_up_sessions():
        while True:
            session_coll.update_many({'deadline': {'$lt': datetime.now()}, 'closed': False}, {'$set': {'closed': True}})
            session_coll.delete_many({'deadline': {'$lt': datetime.now() - timedelta(days=1)}})
            sleep(1)

    @staticmethod
    def get_all_sessions():
        return list(session_coll.find({}, {'_id': 0, 'password': 0, 'questions': 0}))
