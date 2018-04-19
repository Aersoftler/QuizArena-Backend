import os

import yaml

import __root__

with open(os.path.join(__root__.path(), 'credentials.yml'), 'r') as stream:
    creds = yaml.load(stream)
    api_key = creds['api']
    mongo_creds = creds['mongo']
