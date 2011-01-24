# Copyright (c) Ecometrica. All rights reserved.
# Distributed under the BSD license. See LICENSE for details.
import datetime as dt
from decimal import Decimal
import json
import re

from django.db import models
from django.db.models.query import QuerySet
from django.http import HttpResponse

from wapiti import helpers

# ISO 8601
DATE_RE = re.compile('([0-9]{4}-[0-1]?[0-9]-[0-3]?[0-9])')
DATE_FORMAT = '%Y-%m-%d'

class ModelNotRegisteredError(Exception):
    pass
 
HTML_STYLE = (
    """<style type="text/css">
    td { 
        border-top: navy solid thin;
        border-collapse: collapse;
        #border-right: navy solid thin;
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
            m = helpers._registered_types[value['type']].model
        except KeyError:
            raise ModelNotRegisteredError()
        value.pop('type')
        return m.objects.get(**value)

class Encoder(object):
    def __init__(self, format, jsonp=None):
        self.format = format
        self.encode = getattr(self, format)
        self.jsonp = jsonp

    def json(self, value):
        resp = json.dumps(self.convert(value))
        if self.jsonp:
            jsonp = re.sub(r'[^a-zA-Z0-9_]', '', self.jsonp)
            resp = u'%s(%s)'%(jsonp, resp)
        return HttpResponse(resp, mimetype='application/json; charset=utf-8')

    def html(self, value):
        converted = self.convert(value)
        return HttpResponse(
            '<html><head>%(style)s</head><body>%(body)s</body></html>' % {
                'style': HTML_STYLE,
                'body': self.to_html(converted)
            }, 
            mimetype='text/html; charset=utf-8'
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
        
    def convert(self, value):
        # recursively encode objects and dates

        if isinstance(value, (list, QuerySet, tuple, set)):
            value = [self.convert(i) for i in value]
        elif isinstance(value, models.Model):
            value = self.object_to_dict(value)
        elif isinstance(value, dict):
            for k, v in value.iteritems():
                value[k] = self.convert(v)
        elif isinstance(value, dt.date):
            value = value.strftime(DATE_FORMAT)
        elif isinstance(value, Decimal):
            value = float(value)
        elif hasattr(value, 'to_wapiti'):
            value = self.convert(value.to_wapiti())

        return value

    def object_to_dict(self, value):
        for k, v in helpers._registered_types.iteritems():
            if isinstance(value, v.model):
                type_name = k
                api = v.api
                break
        try:
            api_str = value.__api_unicode__()
        except AttributeError:
            api_str = unicode(value)

        obj_dict = {'type': type_name, 'id': value.id, 'str': api_str}
        for f in api.object_repr_fields:
            obj_dict[f] = eval('value.' + f)
        return obj_dict

