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
    # the queryset that will be used for all direct accesses to these objects,
    # such as object views or calling an instance method
    # you could create a custom queryset class to allow for an api
    # type that doesn't map to an actual django type, or simply use this
    # to filter objects available through the api
    # left out so you can hook it up lazily
    # objects = None

    # queryset/manager to use when searching; this allows you to setup a more restricted
    # set of objects when searching, while objects above would be wider, and allow older
    # references to still be valid when used directly
    # if not overridden, the above objects attribute will be used for searches too
    #search_objects = None
    
