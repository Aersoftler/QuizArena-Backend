import json
from datetime import datetime

from bson import ObjectId


class JSONEncoder(json.JSONEncoder):

    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        if isinstance(o, datetime):
            return str(int(o.timestamp() * 1000))
        return json.JSONEncoder.default(self, o)
