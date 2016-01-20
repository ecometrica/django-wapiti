# Copyright (c) Ecometrica. All rights reserved.
# Distributed under the BSD license. See LICENSE for details.
from collections import namedtuple
from decorator import decorator
import sys

from django.apps import apps

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

    api = modelapi()
    api.objects = getattr(api, 'objects', api.model.objects)
    api.search_objects = getattr(api, 'search_objects', api.objects)
    _registered_types[name] = _RegisteredType(api=api)


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
    for app in apps.get_app_configs():
        try:
            __import__(
                '{}.{}'.format(app.name, 'api'), globals(), locals()
            )
        except ImportError:
            pass


def register_models():
    _register_models()
