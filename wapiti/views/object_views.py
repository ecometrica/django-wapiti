# Copyright (c) Ecometrica. All rights reserved.
# Distributed under the BSD license. See LICENSE for details.

from django.db.models import Q

from wapiti import helpers
from wapiti.views.base_view import WapitiBaseView
from wapiti.exceptions import *

class WapitiTypeBaseView(WapitiBaseView):
    def dispatch(self, request, ver, type, *args, **kwargs):
        # check if type is registered barf if not
        try:
            self.model = helpers._registered_types[type].api.model
            self.api = helpers._registered_types[type].api
        except KeyError:
            return APINotFound().get_resp()
        return super(WapitiTypeBaseView, self).dispatch(request, ver, type, 
                                                        *args, **kwargs)

class ObjectOrClassMethodView(WapitiTypeBaseView):
    def get(self, request, ver, type, id_or_method, *args, **kwargs):
        
        # determine if id_or_method is an id, call object_view if so
        if helpers._is_id(id_or_method):
            return self._object_view(request, type, id_or_method)
        else:
            # otherwise call class_method
            return self._class_method(request, type, id_or_method)

    def _object_view(self, request, type, id):
        try:
            return self.api.objects.get(id=id)
        except (self.model.DoesNotExist, ValueError):
            return APINotFound("%s with id %s not found" % (type, id))

    def _class_method(self, request, type, method):

        # check if method exists
        try:
            # note: this looks dangerous - the type and method are passed from the
            # client - but the urls definition prevents any other char than
            # [a-zA-Z_]
            m = eval('self.model.' + method)
        except AttributeError:
            return APINotFound("No method %s on type %s" % (method, type))

        # check if method is registered with the API
        try:
            if not m.api:
                return APIForbidden("Method not available through API")
        except AttributeError:
            return APIForbidden("Method not available through API")
        
        # check if method is a class method
        if m.im_self is not self.model:
            return APINotFound("Method is an instance method")

        return m(**self.args)

def _parse_order_by(results, order_by):
    if order_by.startswith('LENGTH:'):
        field_name = order_by.split(':')[1]
        results = results.extra(
            select={'FIELD_LENGTH':'Length(%s)'%field_name})
        order_by = 'FIELD_LENGTH'
    else:
        order_by = order_by
    return results.order_by(order_by)

class SearchView(WapitiTypeBaseView):
    """
    Search objects of this type on arbitrarily complex queries

    Query is a list of lists and operators, each list containing the field to 
    search for, the search type and the search term. Example queries:
        [["name", "iexact", "Long-haul, business"]]
        [["name", "iexact", "Long-haul, business"], 
         or, ["name", "icontains", "short-haul"]]
    Supported search types: 
        "equal"/"iexact": case-sensitive/insensitive full string match 
                          or "equal" for numerical equality, 
        "contains"/"icontains": case-sensitive/insensitive substring match, 
        "regex"/"iregex": regular expression case-sensitive/insensitive 
                          string match, 
        "lt"/"gt": less-than, greater-than numerical search
    You can't follow foreign or reverse keys.
    """
        
    _CONDITIONS = {'not': '__invert__', 'and': '__and__', 'or': '__or__'}

    def get(self, request, ver, type, *args, **kwargs):
        
        return self._search(request, type)
    
    def _search(self, request, type):
        # parse search query
        query = self.args['query']
        if not query:
            raise APIPoorlyFormedQuery('')
        query_q = self._parse_search_query(query)
        search_results = self.api.search_objects.filter(query_q)
        search_results = _parse_order_by(search_results, self.api.order_by)
        search_results = search_results.distinct()
        return search_results


    def _parse_search_query(self, query):
        if not query:
            return Q()

        elif (isinstance(query, list) and len(query) == 3 
              and isinstance(query[0], (str, unicode))
              and isinstance(query[1], (str, unicode))):
            # this is a query atom, such as ["foo","contains","bar"]
            if ('__' in query[0] 
                and query[0][:query[0].rfind('__')] 
                not in self.api.traversable_fields):

                    raise APIEvilQuery(
                        "You tried following %s but only %s are traversable."%(
                            query[0].split('__')[0], ', '.join(self.api.traversable_fields)
                        )
                    )
            return Q(**{'__'.join(query[:2]) : query[2]})

        elif isinstance(query, list):
            # query contains atoms and conditions
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


class AutoCompleteView(WapitiTypeBaseView):
    """
    Search suitable for auto-completion of user-entered partial strings

    Partial is a string to be searched for in a case-insensitve fashion. 
    The fields that will be searched are defined per-type.
    """
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
        results = self.api.search_objects.filter(search_q)
        results = _parse_order_by(results, self.api.order_by)
        results = results.distinct()
        return list(results)



class InstanceMethodView(WapitiTypeBaseView):
    def get(self, request, ver, type, id, method):

        # check if object exists
        try:
            self.obj = self.api.objects.get(id=id)
        except self.model.DoesNotExist:
            return APINotFound("No such object")
        except ValueError:
            return APINotFound("No such object: malformed id")

        # check if method exists
        try:
            # note: this looks dangerous - the type and method are passed from the
            # client - but the urls definition prevents any other char than
            # [a-zA-Z_]
            self.method = eval('self.obj.' + method)
        except AttributeError:
            return APINotFound("No such method available through the API")

        # check if method is registered with the API
        try:
            if not self.method.api:
                return APIForbidden("Method not available through API")
        except AttributeError:
            return APIForbidden("Method not available through API")

        # check if method is an instance method
        if self.method.im_self is self.model:
            return APINotFound("Method is a class method")

        return self.method(**self.args)

