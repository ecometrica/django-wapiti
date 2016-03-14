# Copyright (c) Ecometrica. All rights reserved.
# Distributed under the BSD license. See LICENSE for details.
import datetime as dt
from decimal import Decimal
from inspect import getargspec
import json
import re
import warnings

from django.db import models
from django.db.models.fields.files import FieldFile
from django.db.models.query import QuerySet
from django.http import HttpResponse

from wapiti import helpers
from wapiti.modelapi import ModelApi

# ISO 8601
DATE_RE = re.compile('((?<!")[0-9]{4}-[0-1]?[0-9]-[0-3]?[0-9](?!"))')
DATE_FORMAT = '%Y-%m-%d'

class ModelNotRegisteredError(Exception):
    pass
 
HTML_STYLE = (
    """<style type="text/css">
    body {
        font-family: Helvetica;
        font-size: 9px;
    }

    table {
        width: 100%;
    }

    table tr td {
        vertical-align: top;
        padding: 4px;
        margin: 0px;
        font-weight: bold;
    }

    table tr td table {
        width: 900px;
        border: none;
        border-bottom: 1px solid #666;
    }
    table tr td table tr td table {
        width: 700px;
        border: none;
        border-top: 1px solid #aaa;
    }
    table tr td table tr td {
        font-weight: normal;
    }

    table tr td table tr td table tr td {
        border-bottom: 1px solid #aaa;
        font-weight: normal;
    }
    table tr td table tr td table tr td table {
        width: 500px;
        border: none;
    }

    table tr td table tr td table tr td table tr td table {
        width: 300px;
        border: none;
    }
    table tr td table tr td table tr td table tr td table tr td {
        border: none;
        font-weight: normal;
        padding: 0px;
        font-size: 0.8em;
    }

    </style>
    """
)
class EcoJSONDecoder(json.JSONDecoder):
    def decode(self, s):
        try:
            return super(EcoJSONDecoder, self).decode(s)
        except ValueError:
            return None

class Decoder(object):
    def __init__(self, format):
        self.format = format
        self.decode = getattr(self, format)

    def json(self, value):
        #FIXME detect dates and turn to string
        value = DATE_RE.subn(r'"\1"', value)[0]
        _decoded = json.loads(value, 'UTF-8', EcoJSONDecoder)
        _parsed = self.convert(_decoded)
        return _parsed
    
    def html(self, value):
        return self.json(value)
        
    def convert(self, value):
        # recursively decode objects and dates

        if isinstance(value, list):
            value = [self.convert(i) for i in value]
        elif isinstance(value, dict):
            for k, v in value.iteritems():
                value[k] = self.convert(v)
            if 'type' in value:
                try:
                    value = self.dict_to_object(value)
                except ModelNotRegisteredError:
                    # If we can't convert this dict to a model object,
                    # keep it as a dict.
                    pass
        elif isinstance(value, (str, unicode)) and DATE_RE.match(value):
            value = dt.datetime.strptime(value, DATE_FORMAT).date()
        return value

    def dict_to_object(self, value):
        try:
            m = helpers._registered_types[value['type']].api
        except KeyError:
            raise ModelNotRegisteredError()
        value.pop('type')
        if 'str' in value:
            value.pop('str')
        return m.objects.get(**value)

class Encoder(object):
    def __init__(self, format, jsonp=None, serialize_all_fields=False,
                 file_handler=None, max_depth=1):
        """
        Constructor, sets up Encoder behavior

        format: format to output (e.g. json)
        jsonp: in case the output needs to be wrapped in a jsonp method, give
               the method name here
        serialize_all_fields: by default, when encountering an object, the 
                              serializer will output a dict with the type, id,
                              repr() and only the fields in the ModelApi's
                              repr_object_fields list. Set this to true to 
                              override this and serialize all the fields
        file_handler: If set to a callable, the encoder will call this for 
                      outside code to do something with the file for filefields
                      and its descendants. The filefield will be passed as an argument.
        max_depth: when serialiazing fields pointing to other objects, the
                   serializer will recurse to at most max_depth depth
        """
        self.format = format
        self.encode = getattr(self, format)
        self.jsonp = jsonp
        self.serialize_all_fields = serialize_all_fields
        self.max_depth = max_depth
        self.file_handler = file_handler
        filehandler_args = getargspec(self.file_handler)[0]
        self._filehandler_backwards_compat = len(filehandler_args) > 1

    def to_json(self, value):
        return json.dumps(self.convert(value))

    def json(self, value):
        resp = self.to_json(value)
        if self.jsonp:
            jsonp = re.sub(r'[^a-zA-Z0-9_]', '', self.jsonp)
            resp = u'%s(%s)'%(jsonp, resp)
        return HttpResponse(resp, content_type='application/json; charset=utf-8')

    def html(self, value):
        converted = self.convert(value)
        return HttpResponse(
            '<html><head>%(style)s</head><body>%(body)s</body></html>' % {
                'style': HTML_STYLE,
                'body': self.to_html(converted)
            }, 
            content_type='text/html; charset=utf-8'
        )
    
    def to_html(self, value):
        if isinstance(value, (list, tuple, set)):
            if not len(value):
                html = '<em>none</em>'
            html = ('<table>'
                    + '\n'.join(['<tr><td>%s</td></tr>' % self.to_html(v)
                                 for v in value])
                    + '</table>')
        elif isinstance(value, dict):
            html = ('<table>'
                    + '\n'.join(['<tr><td>%s</td><td>%s</td></tr>' 
                                 % (self.to_html(k), self.to_html(v))
                                 for k, v in value.iteritems()])
                    + '</table>')
        elif value is None:
            html = u'<em>None</em>'
        else:
            html = (u'%s'%value).replace('\n', '<br/>')

        return html
        
    def convert(self, value, depth=1):
        # recursively encode objects and dates
        # the depth is used to monitor the recursion depth in the case 
        # of fields in a model which contain other model objects, such as
        # a FK. But because after the initial conversion, the encoder
        # will not encode all the object's fields even if serialize_all_fields
        # was True on the Encoder, this will only kick in if the ModelApi for 
        # that model had a FK/M2M/O2M field in its repr_object_fields

        if isinstance(value, (list, QuerySet, tuple, set)):
            value = [self.convert(i, depth) for i in value]
        elif isinstance(value, models.Model):
            if (depth == 1 and self.serialize_all_fields 
                and depth <= self.max_depth):
                value = self.convert(self.object_to_dict(value, all_fields=True),
                                     depth + 1)
            elif depth <= self.max_depth:
                value = self.convert(self.object_to_dict(value, all_fields=False),
                                     depth + 1)
            else:
                value = self.object_to_dict(value, all_fields=False)
        elif isinstance(value, dict):
            for k, v in value.iteritems():
                value[k] = self.convert(v, depth)
        elif isinstance(value, dt.date):
            value = value.strftime(DATE_FORMAT)
        elif isinstance(value, Decimal):
            value = float(value)
        elif isinstance(value, FieldFile):
            try:
                if callable(self.file_handler):
                    if self._filehandler_backwards_compat:
                        warnings.warn(
                            "3-arg form of file_handle is deprecated; "
                            "only the first argument is necessary",
                            DeprecationWarning)
                        self.file_handler(value, value.name, value.path)
                    else:
                        self.file_handler(value)
                value = {'file': value.name}
            except ValueError:
                value = {'file': None}
        elif hasattr(value, 'to_wapiti'):
            value = self.convert(value.to_wapiti(), depth)

        return value

    def object_to_dict(self, value, all_fields=False):
        for k, v in helpers._registered_types.iteritems():
            if isinstance(value, v.api.model):
                type_name = k
                api = v.api
                break
        else:
            type_name = value.__class__.__name__
            api = ModelApi()
        try:
            api_str = value.__api_unicode__()
        except AttributeError:
            api_str = unicode(value)

        obj_dict = {'type': type_name, 'id': value.pk, 'str': api_str}
        if all_fields:
            fields = [f.name for f in value._meta.fields if f.name not in api.invisible_fields]
        else:
            fields = api.object_repr_fields

        for f in fields:
            # object_repr_fields is referring to fields in a different model, which is fine
            # but leaving the dot in the field name sent is not nice on the other end,
            # particularly in python-land where you'll need to getattr everything
            key = f.replace('.', '__')
            obj_dict[key] = eval('value.' + f)
        return obj_dict

