from collections import namedtuple
from functools import wraps

from django.db.models import get_apps
from piston.utils import rc

from ecoapi.conf import ID_RE
from ecoapi.models import APIKey

_RegisteredType = namedtuple('RegisteredType', ('model', ))

_registered_types = {}

def register(name, modelapi):
    """Register a model with the API"""
    global _registered_types
    if modelapi.__name__ in _registered_types:
        return

    _registered_types[name] = _RegisteredType(model=modelapi)

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

def _check_perms(request):
    """Checks if requester api key has permissions for this request"""
    try:
        apikey = APIKey.objects.get(key=request.GET['k'])
    except (KeyError, APIKey.DoesNotExist):
        return False

    return apikey.is_authorized(request)

