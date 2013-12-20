# encoding: utf-8
# Copyright (c) Ecometrica. All rights reserved.
# Distributed under the BSD license. See LICENSE for details.
"""API exception definitions for wapiti"""
import traceback

from django.conf import settings
from django.http import HttpResponse


class APIBaseException(Exception):
    name = "API Error"
    def __init__(self, msg='', code=500):
        self.msg, self.code = msg, code

    def __unicode__(self):
        return u"%d %s %s" % (self.code, self.name, self.msg)

    def get_resp(self):
        resp = HttpResponse(content=self.__unicode__(), status=self.code,
                            content_type='text/plain')
        resp.status_code = self.code
        return resp


class APINotFound(APIBaseException):
    name = "Not Found"
    def __init__(self, msg=''):
        super(APINotFound, self).__init__(msg, 404)

class APINotImplemented(APIBaseException):
    name = "Not Implemented"
    def __init__(self, msg=''):
        super(APINotImplemented, self).__init__(msg, 501)

class APIForbidden(APIBaseException):
    name = "Forbidden"
    def __init__(self, msg=''):
        super(APIForbidden, self).__init__(msg, 403)

class APIRateLimit(APIBaseException):
    name = "Rate Limited"
    def __init__(self, msg=''):
        super(APIRateLimit, self).__init__(msg, 420)

class APIMissingParameter(APIBaseException):
    name = "Missing Parameter(s)"
    def __init__(self, msg='', parameter='', all_parameters=()):
        super(APIMissingParameter, self).__init__(msg, 400)
        self.msg += "\nParameter missing: " + parameter
        if all_parameters:
            self.msg = (self.msg + "\nRequired parameters: "
                        + ' '.join(all_parameters))

class APIServerError(APIBaseException):
    name = "Server Error"
    def __init__(self, msg=''):
        super(APIServerError, self).__init__(msg, 500)
        if settings.DEBUG:
            self.msg += u"\nTraceback:\n " + traceback.format_exc().encode('utf-8')

class APIFormatNotSupported(APIBaseException):
    name = "Requested Format Not Supported"
    def __init__(self, msg='', format=''):
        super(APIFormatNotSupported, self).__init__(msg, 406)
        self.msg += " Format %s not in supported formats (%s)" % (
            format, ', '.join(SUPPORTED_FORMATS)
        )

class APICantGrokParameter(APIBaseException):
    name = "Can't Parse Parameter(s)"
    def __init__(self, msg='', parameter='', value=''):
        super(APICantGrokParameter, self).__init__(msg, 400)
        self.msg += " I can't decode parameter %s=%s" % (parameter, value)
        if settings.DEBUG:
            self.msg += "\nTraceback:\n " + traceback.format_exc()

    def __unicode__(self):
        return u"%d Can't grok: %s" % (self.code, self.msg)

class APIMethodNotAllowed(APIBaseException):
    name = "Method Not Allowed"
    def __init__(self, msg='', method='', allowed=()):
        super(APIMethodNotAllowed, self).__init__(msg, 405)
        self.msg = (self.msg + u" Method %s is not allowed." % method)
        if allowed:
            self.msg = self.msg + " Allowed methods are: " + ', '.join(allowed)

class APIBadSlice(APIBaseException):
    name = "Incorrect Slicing Parameters"
    def __init__(self, msg='', method='', allowed=()):
        super(APIBadSlice, self).__init__(msg, 416)
        self.msg = (self.msg + u" Bad slicing specification, or too much data requested.")

class APIPoorlyFormedQuery(APIBaseException):
    name = "Poorly Formed Query"

    def __init__(self, query_str='', msg=''):
        from wapiti.views.object_views import SearchView
        super(APIPoorlyFormedQuery, self).__init__(msg, 400)
        self.msg += (
            "\nMalformed query string (empty, or invalid json): "
            + query_str + '\n\n' + SearchView.__doc__
        )

class APIEvilQuery(APIBaseException):
    name = "Evil Query"

    def __init__(self, query_str='', msg=''):
        from wapiti.views.object_views import SearchView

        super(APIEvilQuery, self).__init__(msg, 400)
        self.msg += (
            "\nYour query is evil. Following keys is not permitted: "
            + query_str + '\n\n' + SearchView.__doc__
        )


