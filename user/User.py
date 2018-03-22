from database.database import user_coll
from quizarena_utils import hash_password
from shared.Messages import Errors as err


class User:

    def __init__(self, user_id: str, display_name: str = None, password: str = None, total_score: int = 0):
        self.id = user_id
        self.display_name = display_name if display_name is not None else user_id
        self.password = password
        self.total_score = total_score
        self.password_hashed = False

    def register(self):
        if self.password is None:
            raise ValueError(err.NO_PW)
        self.__create_password()
        db_dict = self.__dict__
        del db_dict['password_hashed']
        return user_coll.insert(db_dict)

    def update_display_name(self):
        if self.display_name is None:
            raise ValueError(err.NO_DISPLAY_NAME)
        if self.get() is None:
            raise ValueError(err.NOT_EXISTING_USER)
        return self.update('display_name')

    def update_password(self):
        if self.password is None:
            raise ValueError(err.NO_PW)
        self.__create_password()
        return self.update('password')

    def update_password_api(self, old_password: str):
        user = self.get()
        if user is None:
            raise ValueError(err.NOT_EXISTING_USER)
        if user['password'] != hash_password(old_password):
            raise ValueError(err.OLD_PW_MISMATCH)
        self.update_password()

    def update(self, field: str):
        return user_coll.update({'id': self.id}, {'$set': {field: self.__dict__[field]}})

    def add_total_score(self, score: int):
        if self.get() is None:
            raise ValueError(err.NOT_EXISTING_USER)
        return user_coll.update({'id': self.id}, {'$inc': {'total_score': score}})

    def __create_password(self):
        if not self.password_hashed:
            self.password = hash_password(self.password)
            self.password_hashed = True

    def get(self):
        return user_coll.find_one({'id': self.id})

    def get_api(self):
        return user_coll.find_one({'id': self.id}, {'_id': 0, 'password': 0})
