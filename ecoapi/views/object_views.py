from piston.handler import AnonymousBaseHandler
from piston.resource import Resource
from piston.utils import rc

from ecoapi import helpers
from ecoapi import handlers
from ecoapi.views.base_view import EcoApiBaseView

class EcoApiTypeBaseView(EcoApiBaseView):
    def dispatch(self, request, ver, type, *args, **kwargs):
        # check if type is registered barf if not
        try:
            self.model = helpers._registered_types[type].model
        except KeyError:
            return rc.NOT_FOUND
        return super(EcoApiTypeBaseView, self).dispatch(request, ver, type, *args, **kwargs)

class ObjectOrClassMethodView(EcoApiTypeBaseView):
    def get(self, request, ver, type, id_or_method, *args, **kwargs):
        
        # determine if id_or_method is an id, call object_view if so
        if helpers._is_id(id_or_method):
            return self._object_view(request, type, id_or_method)
        else:
            # otherwise call class_method
            return self._class_method(request, type, id_or_method)

    def _object_view(self, request, type, id):
        return rc.NOT_IMPLEMENTED

    def _class_method(self, request, type, method):
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

        return m(**self.args)

class InstanceMethodView(EcoApiTypeBaseView):
    def get(self, request, ver, type, id, method):

        # check if object exists
        try:
            self.obj = self.model.objects.get(id=id)
        except model.DoesNotExist:
            return rc.NOT_FOUND

        # check if method exists
        try:
            # note: this looks dangerous - the type and method are passed from the
            # client - but the urls definition prevents any other char than
            # [a-zA-Z_]
            self.method = eval('self.obj.' + method)
        except AttributeError:
            return rc.NOT_FOUND

        # check if method is registered with the API
        try:
            if not self.method.api:
                return rc.FORBIDDEN
        except AttributeError:
            return rc.FORBIDDEN
        
        # check if method is an instance method
        if self.method.im_self is self.model:
            return rc.NOT_FOUND

        # create piston handler resource and call it
        return self.method(**self.args)

