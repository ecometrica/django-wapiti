# Copyright (c) Ecometrica. All rights reserved.
# Distributed under the BSD license. See LICENSE for details.
from collections import namedtuple
from decorator import decorator
from functools import wraps
import sys

from django.db.models import get_apps
from piston.utils import rc

from wapiti.conf import ID_RE

_RegisteredType = namedtuple('RegisteredType', ('api', ))

_registered_types = {}

def register(name, modelapi):
    """Register a model with the API"""
    global _registered_types
    if len(sys.argv) > 1 and sys.argv[1] in ('syncdb', 'migrate'):
        return
    if modelapi.__name__ in _registered_types:
        return

    _registered_types[name] = _RegisteredType(api=modelapi())

def _api_method(f, *args, **kwargs):
    return f(*args, **kwargs)

def api_method(f):
    """Decorator to declare a method api-accessible"""
    f.api = True
    return decorator(_api_method, f)

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

def register_models():
    _register_models()

