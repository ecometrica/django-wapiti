from collections import namedtuple
from functools import wraps

from django.db.models import get_apps
from piston.utils import rc

from ecoapi.conf import ID_RE

_RegisteredType = namedtuple('RegisteredType', ('model', 'api'))

_registered_types = {}

def register(name, modelapi):
    """Register a model with the API"""
    global _registered_types
    if modelapi.__name__ in _registered_types:
        return
    if not modelapi.objects:
        modelapi.objects = modelapi.model.objects

    _registered_types[name] = _RegisteredType(model=modelapi.model, 
                                              api=modelapi)

def api_method(f):
    """Decorator to declare a method api-accessible"""
    f.api = True
    @wraps(f)
    def wrapper(*args, **kwargs):
        return f(*args, **kwargs)
    return wrapper

def _is_id(id):
    return ID_RE.match(id)

def _register_models():
    """Find app api submodules and register models"""
    for a in get_apps():
        try:
            _temp = __import__('.'.join(a.__name__.split('.')[:-1] + ['api']), 
                               globals(), locals())
        except ImportError:
            pass


