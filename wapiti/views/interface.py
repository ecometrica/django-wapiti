# Copyright (c) Ecometrica. All rights reserved.
# Distributed under the BSD license. See LICENSE for details.
import inspect

from django.core.urlresolvers import reverse

from piston.utils import rc

from wapiti import helpers
from wapiti.views.base_view import WapitiBaseView

class TopLevelInterfaceView(WapitiBaseView):
    def get(self, request):
        return rc.NOT_IMPLEMENTED

class InterfaceView(WapitiBaseView):
    def get(self, request, ver):
        types = {}
        for name, rt in helpers._registered_types.iteritems():
            methods = {}
            # FIXME: hardcode generic class methods
            search_url = reverse('search', kwargs={'ver' : ver, 'type' : name})
            methods['search'] = {
                'doc': '',
                'args': ('query', ),
                'type': 'class method',
                'url': search_url,
            }
            ac_url = reverse('search', kwargs={'ver' : ver, 'type' : name})
            methods['auto_complete'] = {
                'doc': '',
                'args': ('partial', ),
                'type': 'class method',
                'url': ac_url,
            }
            for m in inspect.getmembers(rt.model):
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

                    methods[m[0]] = {
                        'doc': m[1].__doc__,
                        'args': m[1].im_func.func_code.co_varnames[1:],
                        'type': method_type,
                        'url': url,
                    }
            types[name] = {
                'doc': rt.model.__doc__,
                'methods': methods,
            }
        return types

