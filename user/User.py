from database.database import user_coll
from quizarena_utils import hash_password


class User:

    def __init__(self, user_id: str, display_name: str = None, password: str = None, total_score: int = 0):
        self.id = user_id
        self.display_name = display_name if display_name is not None else user_id
        self.password = password
        self.total_score = total_score
        self.password_hashed = False

    def register(self):
        if self.password is None:
            raise ValueError('Cannot register user without password')
        self.__create_password()
        db_dict = self.__dict__
        del db_dict['password_hashed']
        return user_coll.insert(db_dict)

    def update_display_name(self):
        if self.display_name is None:
            raise ValueError('\'display_name\' cannot be None')
        return self.update('display_name')

    def update_password(self):
        if self.password is None:
            raise ValueError('Password cannot be None')
        self.__create_password()
        return self.update('password')

    def update_password_api(self, old_password: str):
        if self.get()['password'] != hash_password(old_password):
            raise ValueError('Wrong old password')
        self.update_password()

    def update(self, field: str):
        return user_coll.update({'id': self.id}, {'$set': {field: self.__dict__[field]}})

    def add_total_score(self, score: int):
        return user_coll.update({'id': self.id}, {'$inc': {'total_score': score}})

    def __create_password(self):
        if not self.password_hashed:
            self.password = hash_password(self.password)
            self.password_hashed = True

    def get(self):
        return user_coll.find_one({'id': self.id})

    def get_api(self):
        return user_coll.find_one({'id': self.id}, {'_id': 0, 'password': 0})
