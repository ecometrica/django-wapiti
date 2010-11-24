# Copyright (c) Ecometrica. All rights reserved.
# Distributed under the BSD license. See LICENSE for details.
import copy
import json
import inspect

from piston.utils import rc

from django import http
from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.http import HttpResponse
from django.template import RequestContext, loader
from django.utils.translation import ugettext_lazy as _
from django.utils.functional import update_wrapper

from wapiti import helpers
from wapiti.models import APIKey
from wapiti.parsers import Decoder, Encoder

class classonlymethod(classmethod):
    def __get__(self, instance, owner):
        if instance is not None:
            raise AttributeError("This method is available only on the view class.")
        return super(classonlymethod, self).__get__(instance, owner)

class View(object):
    """
    Intentionally simple parent class for all views. Only implements
    dispatch-by-method and simple sanity checking.
    """
    # adapted from django 1.3's base class view

    http_method_names = ['get', 'post', 'put', 'delete', 'head', 'options', 'trace']

    def __init__(self, **kwargs):
        """
        Constructor. Called in the URLconf; can contain helpful extra
        keyword arguments, and other things.
        """
        # Go through keyword arguments, and either save their values to our
        # instance, or raise an error.
        for key, value in kwargs.iteritems():
            setattr(self, key, value)

    @classonlymethod
    def as_view(cls, **initkwargs):
        """
        Main entry point for a request-response process.
        """
        # sanitize keyword arguments
        for key in initkwargs:
            if key in cls.http_method_names:
                raise TypeError(u"You tried to pass in the %s method name as a "
                                u"keyword argument to %s(). Don't do that."
                                % (key, cls.__name__))
            if not hasattr(cls, key):
                raise TypeError(u"%s() received an invalid keyword %r" % (
                    cls.__name__, key))

        def view(request, *args, **kwargs):
            self = cls(**initkwargs)
            return self.dispatch(request, *args, **kwargs)

        # take name and docstring from class
        update_wrapper(view, cls, updated=())

        # and possible attributes set by decorators
        # like csrf_exempt from dispatch
        update_wrapper(view, cls.dispatch, assigned=())
        return view

    def dispatch(self, request, *args, **kwargs):
        # Try to dispatch to the right method; if a method doesn't exist,
        # defer to the error handler. Also defer to the error handler if the
        # request method isn't on the approved list.
        if request.method.lower() in self.http_method_names:
            handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
        else:
            handler = self.http_method_not_allowed
        self.request = request
        return handler(request, *args, **kwargs)

    def http_method_not_allowed(self, request, *args, **kwargs):
        allowed_methods = [m for m in self.http_method_names if hasattr(self, m)]
        sys.stderr.write('Method Not Allowed (%s): %s\n' % (request.method, request.path),
            extra={
                'status_code': 405,
                'request': self.request
            }
        )
        return http.HttpResponseNotAllowed(allowed_methods)

class WapitiBaseView(View):
    def dispatch(self, request, *args, **kwargs):
        # always check API Key permissions
        self.args = {}
        for k, v in request.GET.iteritems():
            self.args[k] = v
        for k, v in request.POST.iteritems():
            self.args[k] = v

        self.api_key = self.args.pop('k', None)

        authorized = True
        try:
            apikey = APIKey.objects.get(key=self.api_key)
        except APIKey.DoesNotExist:
            authorized = False
        else:
            authorized = apikey.is_authorized(request)

        if not authorized:
            resp = rc.FORBIDDEN
            resp.write(" Invalid API key")
            return resp

        self.format = self.args.pop('format', 'json')
        
        # parse the arguments
        self._decoder = Decoder(self.format)
        for k, v in self.args.iteritems():
            self.args[k] = self._decoder.decode(v)

        resp = super(WapitiBaseView, self).dispatch(request, *args, **kwargs)
        if not isinstance(resp, HttpResponse):
            resp = Encoder(self.format).encode(resp)
        return HttpResponse(resp, mimetype="application/%s"%self.format)

class Wapiti404View(View):
    def get(self, request):
        return rc.NOT_FOUND
    
    def put(self, request):
        return rc.NOT_FOUND
    
    def delete(self, request):
        return rc.NOT_FOUND
    
    def post(self, request):
        return rc.NOT_FOUND


