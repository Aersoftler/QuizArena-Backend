import random

from database.database import category_coll, question_coll


class Category:

    def __init__(self, category: str):
        self.category = category

    def add(self):
        return category_coll.insert(self.__dict__)

    def get(self):
        return category_coll.find_one({'category': self.category})

    def get_random_questions(self):
        questions = list(question_coll.find({'category': self.category}))
        indices = random.sample(range(len(questions)), 10)
        return [questions[i]['_id'] for i in indices]

    def exist(self):
        return not self.get() is None

    @staticmethod
    def get_all_categories():
        return list(category_coll.find({}, {'_id': 0}))
