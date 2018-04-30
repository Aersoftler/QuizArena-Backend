import hashlib


def hash_password(password):
    return hashlib.md5(('salt' + password).encode('utf-8')).hexdigest()

# der salt, der hier genutzt wird sollte natürlich nicht im Code stehen, sondern in einem File, welches auch nicht im
# Git liegt
