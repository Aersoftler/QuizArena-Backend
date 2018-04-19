import os
import sys

import yaml

with open(os.path.join(os.path.dirname(sys.modules['__main__'].__file__), 'credentials.yml'), 'r') as stream:
    creds = yaml.load(stream)
    api_key = creds['api']
    mongo_creds = creds['mongo']
