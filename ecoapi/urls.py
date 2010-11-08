from django.conf.urls.defaults import *

from ecoapi.views import *


urlpatterns = patterns('ecoapi.views',
        (r'^/?$', TopLevelInterfaceView.as_view()),
        (r'^(?P<ver>[.0-9]+)/?$', InterfaceView.as_view()),
        (r'^(?P<ver>[.0-9]+)/(?P<type>[a-zA-Z_]+)/(?P<id_or_method>[a-zA-Z_]+)/?$', 
         ObjectOrClassMethodView.as_view()),
        (r'^(?P<ver>[.0-9]+)/(?P<type>[a-zA-Z_]+)/'
         r'(?P<id>[a-zA-Z_]+)/(?P<method>[a-zA-Z_]+)/?$', 
         InstanceMethodView.as_view()),
)

