# Copyright (c) Ecometrica. All rights reserved.
# Distributed under the BSD license. See LICENSE for details.
import inspect

from django.core.urlresolvers import reverse


from wapiti import helpers
from wapiti.exceptions import *
from wapiti.views.base_view import WapitiBaseView
from wapiti.views.object_views import SearchView, AutoCompleteView

class TopLevelInterfaceView(WapitiBaseView):
    def get(self, request):
        return APINotImplemented()

class InterfaceView(WapitiBaseView):
    def get(self, request, ver):
        types = {}
        for name, rt in helpers._registered_types.iteritems():
            methods = {}
            # FIXME: hardcode generic class methods
            search_url = reverse('search', kwargs={'ver' : ver, 'type' : name})
            methods['search'] = {
                'doc': '<pre>' + SearchView.__doc__ + '</pre>',
                'args': ('query', ),
                'type': 'class method',
                'url': search_url,
            }
            ac_url = reverse('auto_complete', 
                             kwargs={'ver' : ver, 'type' : name})
            methods['auto_complete'] = {
                'doc': '<pre>' + AutoCompleteView.__doc__ + '</pre>',
                'args': ('partial', ),
                'type': 'class method',
                'url': ac_url,
            }
            for m in inspect.getmembers(rt.api.model):
                if (inspect.ismethod(m[1])
                    and 'api' in dir(m[1])
                    and m[1].api):
                    if m[1].im_self:
                        # this is a class method
                        method_type = 'class method'
                        url = reverse('object_or_cm_view', 
                                      kwargs={'ver' : ver, 'type' : name, 
                                              'id_or_method' : m[0]})
                    else:
                        method_type = 'instance method'
                        url = reverse('im_view', 
                                      kwargs={'ver' : ver, 'type' : name, 
                                              'id' : 'OBJECT_ID',
                                              'method' : m[0]})

                    doc = (m[1].__doc__ and ('<pre>' + m[1].__doc__ + '</pre>')
                           or '<em>no documentation</em>'),
                    methods[m[0]] = {
                        'doc': doc,
                        'args': m[1].im_func.func_code.co_varnames[1:],
                        'type': method_type,
                        'url': url,
                    }
            types[name] = {
                'doc': rt.api.model.__doc__,
                'methods': methods,
            }
        return types

