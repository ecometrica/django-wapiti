# Copyright (c) Ecometrica. All rights reserved.
# Distributed under the BSD license. See LICENSE for details.
class ModelApi(object):
    # mode this api type is tied to, if any
    model = None
    # the manager - you can override it just for the API
    objects = None
    # fields that should always be returned when serializing the object
    object_repr_fields = []
    # fields to search into for auto_complete
    auto_complete_fields = []
    # auto_complete lookup type
    auto_complete_type = 'icontains'
    # order auto_complete results by
    # this can be 'LENGTH:fieldname' in which case results will be sorted
    # by the length of field fieldname (which should be a string!)
    auto_complete_order_by = 'id'
    # never ever allow modification of these fields, whoever asks
    read_only_fields = []
    # never ever show these fields, whoever asks
    invisible_fields = []
    
