from datetime import datetime, timedelta
from time import sleep
from typing import List

from bson import ObjectId
from pyfcm import FCMNotification

from database.database import session_coll
from quiz.Category import Category
from quiz.Question import Question
from shared.Messages import Errors as err
from shared.hash_password import hash_password
from shared.read_credentials import api_key
from user.User import User

primary_key = '_id'
push_service = FCMNotification(api_key=api_key)


class Session:

    def __init__(self, session_id: str = None, name: str = '', category: str = 'Allgemeinwissen', private: bool = False,
                 password: str = None, questions: List[Question] = list(),
                 deadline: datetime = datetime.now() + timedelta(days=1), users: List[str] = list(),
                 closed: bool = False, admin: str = None):
        self.name = name
        self.category = category
        self.private = private
        self.password = password
        self.questions = questions
        self.deadline = deadline
        self.users = users
        self.closed = closed
        self.password_hashed = False
        self.id = session_id
        self.admin = admin

    def create(self):
        category = Category(self.category)
        if not category.exist():
            raise ValueError(err.NO_MATCHING_CATEGORY.value)
        if type(self.deadline) is not datetime:
            raise TypeError(err.TYPE_MISMATCH.value)
        if len(self.questions) >= 11:
            raise ValueError(err.TOO_MANY_QUESTIONS.value)
        if self.private is True:
            if self.password is None:
                raise ValueError(err.NO_PW_FOR_PRIVATE_SESSION.value)
            self.__create_password()
        self.questions = category.get_random_questions()
        db_dict = self.__dict__
        del db_dict['password_hashed']
        del db_dict['id']
        return session_coll.insert(self.__dict__)

    def remove(self):
        return session_coll.delete_one({primary_key: ObjectId(self.id)})

    def add_user(self, user: User, password: str = ''):
        if not user.exists():
            raise ValueError(err.USER_NOT_FOUND.value)
        self.get_information_to_add_user()
        if self.closed:
            raise ValueError(err.SESSION_ALREADY_CLOSED.value)
        if self.private and self.password != hash_password(password):
            raise PermissionError(err.PW_MISMATCH.value)
        return session_coll.update_one(
            {primary_key: ObjectId(self.id)},
            {'$push': {'users': {'user': user.id, 'score': 0}}}
        )

    def set_users_score(self, user: User, score: int):
        if user.get() is None:
            raise ValueError(err.USER_NOT_FOUND.value)
        return session_coll.update_one(
            {'$and': [{primary_key: ObjectId(self.id)}, {'users.user': user.id}]},
            {'$set': {'users.$.score': score}}
        )

    def remove_user(self, user: User):
        return session_coll.update_one({primary_key: ObjectId(self.id)}, {'$pull': {'users': {'user': user.id}}})

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
            {'$match': {primary_key: ObjectId(self.id)}},
            {'$project': {'password': 0}}
        ]
        return list(session_coll.aggregate(pipeline))

    def get_information_to_add_user(self):
        settings = list(session_coll.find({primary_key: ObjectId(self.id)},
                                          {'_id': 0, 'password': 1, 'private': 1, 'closed': 1}))[0]
        self.password = settings['password']
        self.private = settings['private']
        self.closed = settings['closed']
        return settings['password'], settings['private'], settings['closed']

    def get_users(self):
        session = list(session_coll.find({primary_key: ObjectId(self.id)}, {'_id': 0, 'users': 1}))[0]['users']
        self.users = session
        return session

    def get_users_names(self):
        users = list(session_coll.find({primary_key: ObjectId(self.id)}, {'users.user': 1, primary_key: 0}))[0]['users']
        return [user['user'] for user in users]

    def close_api(self, user: User):
        if not user.exists():
            raise ValueError(err.NOT_EXISTING_USER.value)
        is_admin = session_coll.find_one({primary_key: ObjectId(self.id)}, {primary_key: 0, 'admin': 1})['admin']
        if not is_admin:
            raise PermissionError(err.PERMISSION_DENIED.value)
        self.close()
        return user

    def set_db_name(self):
        self.name = self.name if self.name != '' else \
            session_coll.find_one({primary_key: ObjectId(self.id)}, {primary_key: 0, 'name': 1})['name']

    def close(self):
        self.set_db_name()
        device_ids = self.get_device_tokens()
        messsage_title = self.name + ' wurde beendet!'
        message_body = 'Die Quizarena ' + self.name + ' ist beendet worden. Siehe dir die Ergebnisse an :)'
        push_service.notify_multiple_devices(registration_ids=device_ids,
                                             message_title=messsage_title,
                                             message_body=message_body)
        session_coll.update_one({primary_key: ObjectId(self.id)}, {'$set': {'closed': True}})

    def get_device_tokens(self):
        return User.get_device_tokes_by_user_list(self.get_users_names())

    def get_result(self):
        users = self.get_users()
        for i, user in enumerate(users):
            users[i]['user'] = User(user['user']).get_display_name()
        return users

    @staticmethod
    def tidy_up_sessions():
        while True:
            closing_id = session_coll.find_one({'deadline': {'$lt': datetime.now()}, 'closed': False})
            if closing_id is not None:
                Session(closing_id['_id']).close()
            session_coll.delete_many({'deadline': {'$lt': datetime.now() - timedelta(days=1)}})
            sleep(1)

    @staticmethod
    def get_all_sessions():
        return list(session_coll.find({}, {'password': 0, 'questions': 0}))

    @staticmethod
    def get_session_for_user(user: str):
        return {
            'sessions_i_participate':
                list(session_coll.find({'users.user': user}, {'password': 0, 'questions': 0, 'users': 0})),
            'sessions_to_participate':
                list(session_coll.find({'users.user': {'$ne': user}, 'closed': False},
                                       {'password': 0, 'questions': 0, 'admin': 0, 'users': 0}))
        }
