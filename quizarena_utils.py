import hashlib


def hash_password(password):
    return hashlib.md5(('salt' + password).encode('utf-8')).hexdigest()
