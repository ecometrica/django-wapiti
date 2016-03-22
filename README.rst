===============================
django-wapiti generic api layer
===============================

about
=====

Django-wapiti is a generic API layer that can be added to any django project
to allow other applications to get access to its models and methods very easily
through JSON.

It is being developped by Ecometrica_ and made open source under a BSD license.

status
~~~~~~

Django-wapiti is still under development. What works currently:

* enabling the api for a given model
* accessing objects by id
* searching for objects through any of its fields, using any of the django
  queryset field matching operators (``exact``, ``iexact``, ``contains``, ...)
* auto-complete call allows frontend code to easily auto-complete user-entered
  data; it will search for objects through different fields
* the ModelApi class, like ModelAdmin class for the django admin, is how you 
  define the behavior an object should have through the API
* instance methods are supported: simply decorate the method to make it available
* class methods are also supported in the same manner
* API keys
* limiting requests per-{ip,session,user,apikey} per-{hour,day,month,year,ever}
  per-{http method, object, type, method}
* slicing of results - add slice_left and slice_right parameters to your request to
  slice the results
  * the default max slice size is 100, override with settings.WAPITI_MAX_SLICE_SIZE


short-term plan
~~~~~~~~~~~~~~~

Because we need the following functionality, it likely will be incorporated 
soonish:

* better method for defining the permissions for a given API key
* user authentication (OAuth or otherwise) and row-level permissions
* call logging (for quota and throttling enforcement)
* api introspection: /api/VER/ should return a json (or XML) representation of
  the currently registered models and calls

known bugs
~~~~~~~~~~

* the JSON decoder will interpret both 2010-12-31 and "2010-12-31" as a date; it
  should interpret the latter as a string

usage
=====

#. install django-wapiti. the easiest way might be to use::
   
    pip install git+http://git@github.com/ecometrica/django-wapiti.git#egg=django-wapiti

#. wapiti requires the decorator module to function::
   
    pip install decorator

#. add ``wapiti`` to your INSTALLED_APPS in the settings.py file of your django
   project

#. call wapiti.helpers.register_models from somewhere, usually your urls.py, to
   register your api models and methods

#. to make the model class Foo from the app fooapp available through the API, 
   create a file ``fooapp/api.py`` with this content::

    from wapiti.helpers import register
    from wapiti.modelapi import ModelApi

    from fooapp.models import Foo

    class FooApi(ModelApi):
        auto_complete_fields = ('name', 'description')
        auto_complete_order_by = 'name'
        model = Foo

    register('foo', FooApi)
  
   We've made the auto_complete method work by automatically searching for Foo
   objects with a case-insensitive search on the fields name and description
   (which therefore must exist in the Foo model definition).
   
   See the file ``wapiti/modelapi.py`` for a list of all options available in 
   the ModelApi class for a given model.

#. At this point, all objects of type Foo are available through the API at 
   ``/api/1.0/foo/``. To make an instance method available for calling through 
   the API, apply the ``wapiti.helpers.api_method`` decorator to it. To call
   foo_method on the Foo object with ID 3, you would 
   ``GET /api/1.0/foo/3/foo_method``

#. Similarly, for a class method, just decorate it with that same ``api_method``, 
   but apply the python ``classmethod`` decorator *above* it as well. To call
   the foo_cls_method on Foo through the API you would then
   ``GET /api/1.0/foo/foo_cls_method``

#. To make calls through the API, you'll need API keys. From the main django
   admin interface, click on ``Add APIKey``, add a name, and add a permission 
   with resource_regex ``.*`` on method ``GET``. All API calls need to have a 
   ``k=THEAPIKEY`` parameter with a valid and active API key.

#. All calls through JSON must have all their parameters be proper JSON! This 
   means that to pass a string argument to a method, it needs to be surrounded
   by double-quotes! See the JSON_ spec for details.

#. In order to use per-IP limiting, we need the REMOTE_ADDR variable. If you're
   using nginx, this needs to be in the proper ``location`` section: ::

    fastcgi_param REMOTE_ADDR $remote_addr;
    
Release Notes
=============

v0.0.1
~~~~~~

* Initial version

v0.0.2
~~~~~~
    
* Slicing of results
* Compatible with Django 1.4 to 1.6 

v0.0.3
~~~~~~

* post-South migrations
* Compatible with Django 1.7 to 1.9

v1.0.0
~~~~~~

* Compatible with Django 1.8 and 1.9 (no longer compatible with Django =< 1.7)

v1.0.1
~~~~~~

* File handler now only takes field to better support non-FileSystemStorage
  files. Old way is still supported, but deprecated.

v1.0.2
~~~~~~

* Previous version forgot to handle the case of no file handler being
  supplied. This release fixes that.

.. _Ecometrica: http://ecometrica.com
.. _JSON: http://json.org

