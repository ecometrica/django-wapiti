# Copyright (c) Ecometrica. All rights reserved.
# Distributed under the BSD license. See LICENSE for details.
from django.conf.urls.defaults import *

from wapiti.views import *


urlpatterns = patterns('wapiti.views',
        (r'^/?$', TopLevelInterfaceView.as_view()),
        (r'^(?P<ver>[.0-9]+)/?$', InterfaceView.as_view()),
        (r'^(?P<ver>[.0-9]+)/(?P<type>[a-zA-Z0-9_]+)/search/?$', 
         SearchView.as_view()),
        (r'^(?P<ver>[.0-9]+)/(?P<type>[a-zA-Z0-9_]+)/auto_complete/?$', 
         AutoCompleteView.as_view()),
        (r'^(?P<ver>[.0-9]+)/(?P<type>[a-zA-Z0-9_]+)'
         r'/(?P<id_or_method>[a-zA-Z0-9_]+)/?$', 
         ObjectOrClassMethodView.as_view()),
        (r'^(?P<ver>[.0-9]+)/(?P<type>[a-zA-Z0-9_]+)/'
         r'(?P<id>[a-zA-Z0-9_]+)/(?P<method>[a-zA-Z0-9_]+)/?$', 
         InstanceMethodView.as_view()),
        (r'.*', wapiti404View.as_view()),
)
