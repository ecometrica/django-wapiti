from piston.handler import AnonymousBaseHandler
from piston.resource import Resource
from piston.utils import rc

from django.db.models import Q

from ecoapi import helpers
from ecoapi import handlers
from ecoapi.views.base_view import EcoApiBaseView

class EcoApiTypeBaseView(EcoApiBaseView):
    def dispatch(self, request, ver, type, *args, **kwargs):
        # check if type is registered barf if not
        try:
            self.model = helpers._registered_types[type].model
            self.api = helpers._registered_types[type].api
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

        # check if method exists
        try:
            # note: this looks dangerous - the type and method are passed from the
            # client - but the urls definition prevents any other char than
            # [a-zA-Z_]
            m = eval('self.model.' + method)
        except AttributeError:
            return rc.NOT_FOUND

        # check if method is registered with the API
        try:
            if not m.api:
                return rc.FORBIDDEN
        except AttributeError:
            return rc.FORBIDDEN
        
        # check if method is a class method
        if m.im_self is not self.model:
            return rc.NOT_FOUND

        return m(**self.args)

class SearchView(EcoApiTypeBaseView):
        
    _CONDITIONS = {'not': '__invert__', 'and': '__and__', 'or': '__or__'}

    def get(self, request, ver, type, *args, **kwargs):
        
        return self._search(request, type)
    
    def _search(self, request, type):
        # parse search query
        query_q = self._parse_search_query(self.args['query'])
        search_results = self.api.objects.filter(query_q)
        return list(search_results[:100])


    def _parse_search_query(self, query):
        if not query:
            return Q()

        elif (isinstance(query, list) and len(query) == 3 
              and all(map(lambda i: isinstance(i, (str, unicode)), query))):
            return Q(**{'__'.join(query[:2]) : query[2]})

        elif isinstance(query, list):
            q = None
            cond = '__or__'
            for t in query:
                if isinstance(t, list):
                    new_q = self._parse_search_query(t)
                    if q is None:
                        q = new_q
                    else:
                        q = getattr(q, cond)(new_q)
                else:
                    cond = self._CONDITIONS[t.lower()]
            return q


class AutoCompleteView(EcoApiTypeBaseView):
    def get(self, request, ver, type, *args, **kwargs):
        
        return self._auto_complete(request, type)
    
    def _auto_complete(self, request, type):
        search_str = self.args['partial']
        if not search_str:
            return []

        
        search_q = Q()
        for f in self.api.auto_complete_fields:
            search_d = {'%s__%s' % (f, self.api.auto_complete_type): search_str}
            search_q |= Q(**search_d)
        results = self.api.objects.filter(search_q)
        results = results.order_by(self.api.auto_complete_order_by)
        return list(results)



class InstanceMethodView(EcoApiTypeBaseView):
    def get(self, request, ver, type, id, method):

        # check if object exists
        try:
            self.obj = self.api.objects.get(id=id)
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

