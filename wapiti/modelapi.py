# Copyright (c) Ecometrica. All rights reserved.
# Distributed under the BSD license. See LICENSE for details.
class ModelApi(object):
    # mode this api type is tied to, if any
    model = None
    # fields that should always be returned when serializing the object
    object_repr_fields = []
    # fields to search into for auto_complete
    auto_complete_fields = []
    # auto_complete lookup type
    auto_complete_type = 'istartswith'
    # order auto_complete and search results by
    # this can be 'LENGTH:fieldname' in which case results will be sorted
    # by the length of field fieldname (which should be a string!)
    order_by = 'id'
    # never ever allow modification of these fields, whoever asks
    read_only_fields = []
    # never ever show these fields, whoever asks
    invisible_fields = []
    # fields which can be traversed in search. e.g. to be able to do:
    # ['foofield__name','icontains','BOO']
    # you'll need to put 'foofield' in here
    traversable_fields = []
    # the queryset that will be used for all accesses to these objects
    # you could create a custom queryset class to allow for an api
    # type that doesn't map to an actual django type, or simply use this
    # to filter objects available through the api
    # left out so you can hook it up lazily
    # objects = None
    
