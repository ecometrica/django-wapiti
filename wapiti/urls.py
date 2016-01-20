# Copyright (c) Ecometrica. All rights reserved.
# Distributed under the BSD license. See LICENSE for details.

from django.conf.urls import url
from wapiti.views import (
    TopLevelInterfaceView, InterfaceView, AutoCompleteView, SearchView,
    ObjectOrClassMethodView, InstanceMethodView, Wapiti404View
)


urlpatterns = [
    url(r'^$', TopLevelInterfaceView.as_view(), name='top_level_interface'),
    url(r'^(?P<ver>[.0-9]+)/?$', InterfaceView.as_view(), name='interface'),
    url(r'^(?P<ver>[.0-9]+)/(?P<type>[a-zA-Z0-9_]+)/search/?$',
        SearchView.as_view(), name='search'),
    url(r'^(?P<ver>[.0-9]+)/(?P<type>[a-zA-Z0-9_]+)/auto_complete/?$',
        AutoCompleteView.as_view(), name='auto_complete'),
    url(r'^(?P<ver>[.0-9]+)/(?P<type>[a-zA-Z0-9_]+)'
        r'/(?P<id_or_method>[a-zA-Z0-9_]+)/?$',
        ObjectOrClassMethodView.as_view(), name='object_or_cm_view'),
    url(r'^(?P<ver>[.0-9]+)/(?P<type>[a-zA-Z0-9_]+)/'
        r'(?P<id>[a-zA-Z0-9_]+)/(?P<method>[a-zA-Z0-9_]+)/?$',
        InstanceMethodView.as_view(), name='im_view'),
    url(r'.*', Wapiti404View.as_view(), name='404'),
]
