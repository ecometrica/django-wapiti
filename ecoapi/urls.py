from django.conf.urls.defaults import *

from ecoapi.views import ObjectOrClassMethodView, InstanceMethodView

urlpatterns = patterns('ecoapi.views',
        (r'^/?$', 'generic_interface'),
        (r'^(?P<ver>[.0-9]+)/?$', 'interface'),
        (r'^(?P<ver>[.0-9]+)/(?P<type>[a-zA-Z_]+)/(?P<id_or_method>[a-zA-Z_]+)/?$', 
         ObjectOrClassMethodView.as_view()),
        (r'^(?P<ver>[.0-9]+)/(?P<type>[a-zA-Z_]+)/'
         r'(?P<id>[a-zA-Z_]+)/(?P<method>[a-zA-Z_]+)/?$', 
         InstanceMethodView.as_view()),
)

