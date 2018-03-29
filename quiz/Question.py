from bson import ObjectId

from database.database import question_coll
from quiz.Answers import Answers
from quiz.Category import Category
from shared.Messages import Errors as err


class Question:

    def __init__(self, _id: ObjectId = None, question: str = None, answers: Answers = None, category: str = 'default'):
        self._id = _id
        self.question = question
        self.answers = answers
        self.category = category

    def add(self):
        if type(self.answers) is not dict:
            raise TypeError(err.TYPE_MISMATCH.value)
        if type(self.answers['wrong_answers']) is not list or len(self.answers['wrong_answers']) is not 3:
            raise TypeError(err.ANSWER_COUNT_INVALID.value)
        if Category(self.category).get() is None:
            raise ValueError(err.NO_MATCHING_CATEGORY.value)
        question_dict = self.__dict__
        if self._id is None:
            del question_dict['_id']
        return question_coll.insert(self.__dict__)
