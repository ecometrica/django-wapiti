# Copyright (c) Ecometrica. All rights reserved.
# Distributed under the BSD license. See LICENSE for details.
from collections import defaultdict
import copy
import json
import inspect
import re
import traceback

from piston.utils import rc

from django import http
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.http import HttpResponse
from django.template import RequestContext, loader
from django.utils.translation import ugettext_lazy as _
from django.utils.functional import update_wrapper

from wapiti import helpers
from wapiti.conf import ANONYMOUS_API_KEY
from wapiti.models import APIKey, LogItem
from wapiti.parsers import Decoder, Encoder

SUPPORTED_FORMATS = ('json', 'html')

class APIBaseException(Exception):
    def __init__(self, msg='', code=500):
        self.msg, self.code = msg, code

    def __unicode__(self):
        return u"%d %s" % (self.code, self.msg)
    
    def get_resp(self):
        resp = HttpResponse(content=self.msg, status=self.code)
        return resp


class APIForbidden(APIBaseException):
    def __init__(self, msg=''):
        super(APIForbidden, self).__init__(msg, 403)

    def __unicode__(self):
        return u"%d You can't do that!: %s" % (self.code, self.msg)

class APIRateLimit(APIBaseException):
    def __init__(self, msg=''):
        super(APIRateLimit, self).__init__(msg, 420)

    def __unicode__(self):
        return u"%d You can't do that!: %s" % (self.code, self.msg)

class APIMissingParameter(APIBaseException):
    def __init__(self, msg='', parameter='', all_parameters=()):
        super(APIMissingParameter, self).__init__(msg, 400)
        self.msg += "\nParameter missing: " + parameter
        if all_parameters:
            self.msg = (self.msg + "\nRequired parameters: " 
                        + ' '.join(all_parameters))

    def __unicode__(self):
        return u"%d You forgot one!: %s" % (self.code, self.msg)

class APIServerError(APIBaseException):
    def __init__(self, msg=''):
        super(APIServerError, self).__init__(msg, 500)
        if settings.DEBUG:
            self.msg += "\nTraceback:\n " + traceback.format_exc()

    def __unicode__(self):
        return u"%d Looks like we screwed up: %s" % (self.code, self.msg)

class APIFormatNotSupported(APIBaseException):
    def __init__(self, msg='', format=''):
        super(APIFormatNotSupported, self).__init__(msg, 406)
        self.msg += " Format %s not in supported formats (%s)" % (
            format, ', '.join(SUPPORTED_FORMATS)
        )

    def __unicode__(self):
        return u"%d Lost in translation: %s" % (self.code, self.msg)

class APICantGrokParameter(APIBaseException):
    def __init__(self, msg='', parameter='', value=''):
        super(APICantGrokParameter, self).__init__(msg, 400)
        self.msg += " I can't decode parameter %s=%s" % (parameter, value)
        if settings.DEBUG:
            self.msg += "\nTraceback:\n " + traceback.format_exc()

    def __unicode__(self):
        return u"%d Can't grok: %s" % (self.code, self.msg)

class APIMethodNotAllowed(APIBaseException):
    def __init__(self, msg='', method='', allowed=()):
        super(APIMethodNotAllowed, self).__init__(msg, 405)
        self.msg = (self.msg + u" Method %s is not allowed." % method)
        if allowed:
            self.msg = self.msg + " Allowed methods are: " + ', '.join(allowed)

    def __unicode__(self):
        return u"%d I can't be used that way: %s" % (self.code, self.msg)

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

    http_method_names = ['get', 'post', 'put', 'delete', 'head', 'options', 
                         'trace']

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
            handler = getattr(self, request.method.lower(), 
                              self.http_method_not_allowed)
        else:
            handler = self.http_method_not_allowed
        self.request = request
        return handler(request, *args, **kwargs)

    def http_method_not_allowed(self, request, *args, **kwargs):
        allowed_methods = [m for m in self.http_method_names 
                           if hasattr(self, m)]
        return APIMethodNotAllowed(method=request.method, 
                                   allowed=allowed_methods).get_resp()

class WapitiBaseView(View):
    def dispatch(self, request, *args, **kwargs):
        resp = self._dispatch(request, *args, **kwargs)

        if isinstance(resp, HttpResponse):
            return resp
        elif isinstance(resp, APIBaseException):
            e = resp
            resp = HttpResponse(
                Encoder(self.format, jsonp=self.jsonp).encode(e.msg)
            )
            resp.status_code=e.code
        else:
            try:
                resp = Encoder(self.format, jsonp=self.jsonp).encode(resp)
            except:
                return APIServerError(u"Error encoding the results!").get_resp()

        return resp

    def _dispatch(self, request, *args, **kwargs):
        # always check API Key permissions
        self.args = defaultdict(lambda: '')
        for k, v in request.GET.iteritems():
            self.args[k] = v
        for k, v in request.POST.iteritems():
            self.args[k] = v

        self.format = self.args.pop('format', 'json')
        self.jsonp = self.args.pop('callback', None)
        if self.format not in SUPPORTED_FORMATS:
            return APIFormatNotSupported(format=self.format)
        
        self.api_key = self.args.pop('k', ANONYMOUS_API_KEY)

        authorized = True
        try:
            apikey = APIKey.objects.get(key=self.api_key, active=True)
        except APIKey.DoesNotExist:
            authorized = False
        else:
            authorized = apikey.is_authorized(request)

        if authorized:
            lim = apikey.check_limits(request)
            if lim != True:
                return APIRateLimit("Limit exceeded: %s"%lim)
        else:
            return APIForbidden("Invalid API Key")

        # parse the arguments        
        self._decoder = Decoder(self.format)
        for k, v in self.args.iteritems():
            try:
                self.args[k] = self._decoder.decode(v)
            except:
                return APICantGrokParameter(k, v)

        try:
            resp = super(WapitiBaseView, self).dispatch(request, *args, 
                                                        **kwargs)
        except APIBaseException, e:
            return e
        except Exception, e:
            return APIServerError("Unknown error processing request: " + 
                                  e.__unicode__())
        LogItem.log_api_call(apikey, request, dict(self.args))

        return resp

class Wapiti404View(View):
    def get(self, request):
        return rc.NOT_FOUND
    
    def put(self, request):
        return rc.NOT_FOUND
    
    def delete(self, request):
        return rc.NOT_FOUND
    
    def post(self, request):
        return rc.NOT_FOUND


