from piston.handler import AnonymousBaseHandler
from piston.resource import Resource
from piston.utils import rc

from ecoapi import helpers
from ecoapi import handlers

def object_view_or_class_method(request, ver, type, id_or_method):
    if not helpers._check_perms(request):
        resp = rc.FORBIDDEN
        resp.write(" Invalid API key")
        return resp

    # check if type is registered barf if not
    if type not in helpers._registered_types:
        return rc.NOT_FOUND
    
    # determine if id_or_method is an id, call object_view if so
    if helpers._is_id(id_or_method):
        return _object_view(request, type, id_or_method)
    else:
        # otherwise call class_method
        return _class_method(request, type, id_or_method)

def _object_view(request, type, id):
    return rc.NOT_IMPLEMENTED

def _class_method(request, type, method):
    model = helpers._registered_types[type].model

    # check if method exists
    try:
        # note: this looks dangerous - the type and method are passed from the
        # client - but the urls definition prevents any other char than
        # [a-zA-Z_]
        m = eval('model.' + method)
    except AttributeError:
        return rc.NOT_FOUND

    # check if method is registered with the API
    try:
        if not m.api:
            return rc.FORBIDDEN
    except AttributeError:
        return rc.FORBIDDEN
    
    # check if method is a class method
    if m.im_self is not model:
        return rc.NOT_FOUND

    # create piston handler resource and call it
    class H(handlers.EcoBaseClassHandler):
        allowed_methods = ('GET',)
        cls_method = m

        def read(self, request, *args, **kwargs):
            return self.cls_method(*args, **kwargs)

    return Resource(H)(request, request.GET['src_airport_code'], request.GET['dst_airport_code'])
    

def instance_method(request, ver, type, id, method):
    if not helpers._check_perms(request):
        resp = rc.FORBIDDEN
        resp.write(" Invalid API key")
        return resp

    # check if type is registered barf if not
    try:
        model = helpers._registered_types[type].model
    except KeyError:
        return rc.NOT_FOUND

    # check if object exists
    try:
        o = model.objects.get(id=id)
    except model.DoesNotExist:
        return rc.NOT_FOUND

    # check if method exists
    try:
        # note: this looks dangerous - the type and method are passed from the
        # client - but the urls definition prevents any other char than
        # [a-zA-Z_]
        m = eval('o.' + method)
    except AttributeError:
        return rc.NOT_FOUND

    # check if method is registered with the API
    try:
        if not m.api:
            return rc.FORBIDDEN
    except AttributeError:
        return rc.FORBIDDEN
    
    # check if method is an instance method
    if m.im_self is model:
        return rc.NOT_FOUND

    # create piston handler resource and call it
    class H(handlers.EcoBaseObjectHandler):
        allowed_methods = ('GET',)
        method = m

        def read(self, request, *args, **kwargs):
            return self.method(*args, **kwargs)

    return Resource(H)(request)

