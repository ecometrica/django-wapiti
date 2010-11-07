from collections import namedtuple
from functools import wraps

from django.db.models import get_apps

def new_apikey():
    from ecoapi import APIKEY_ALLOWABLE_LETTERS, APIKEY_LENGTH
    return ''.join(random.sample(APIKEY_ALLOWABLE_LETTERS, APIKEY_LENGTH))

def register(name, modelapi):
    from ecoapi import registered_types, RegisteredType
    if modelapi.__name__ in registered_types:
        return

    registered_types[name] = RegisteredType(model=modelapi)

def api_method(f):
    f.api = True
    @wraps(f)
    def wrapper(*args, **kwargs):
        return f(*args, **kwargs)
    return wrapper

def is_id(id):
    from ecoapi import ID_RE
    return ID_RE.match(id)

def register_models():
    """Find app api submodules and register models"""
    global registered_types
    for a in get_apps():
        try:
            _temp = __import__('.'.join(a.__name__.split('.')[:-1] + ['api']), 
                               globals(), locals())
        except ImportError:
            pass


