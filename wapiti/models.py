# Copyright (c) Ecometrica. All rights reserved.
# Distributed under the BSD license. See LICENSE for details.
import base64
import cPickle as Pickle
import datetime as dt
import random
import re

from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.core.cache import cache
from django.db import models
from django.db.models import F

from wapiti.conf import APIKEY_ALLOWABLE_LETTERS, APIKEY_LENGTH

METHODS = ('GET', 'POST', 'PUT', 'DELETE')

def new_apikey():
    return ''.join(random.sample(APIKEY_ALLOWABLE_LETTERS, APIKEY_LENGTH))

class APIKey(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField()
    key = models.CharField(max_length=32, default=new_apikey)
    active = models.BooleanField(default=True)
    
    def __unicode__(self):
        return u'%s:%s (%s)'%(self.name, self.key, 
                              'act' if self.active else 'dis')

    def _perm_cache_key(self, method):
        return (self.key + '-' + method)

    def flush_permissions_cache(self):
        for m in METHODS:
            cache.delete(self._perm_cache_key(m))

    def is_authorized(self, request):
        q = self.permission_set.filter(
            method = request.method
        )

        if not q:
            return False

        perms_re = cache.get(self._perm_cache_key(request.method))

        if not perms_re:
            perms_re = re.compile(
                '(' 
                + ')|('.join(q.values_list('resource_regex', flat=True)) 
                + ')'
            )
            cache.set(self._perm_cache_key(request.method), perms_re)

        if perms_re.match(request.path):
            return True

        return False
    
    def check_limits(self, request):
        """
        Increments all limit usage counts and check them

        Returns exceeded limit object if any, True if none are exceeded.
        """
        for l in self.limit_set.filter(method=request.method):
            if l.increment_if_matches(self, request):
                return l
        return True

    def save(self, *args, **kwargs):
        # invalidate cached permission regexes
        self.flush_permissions_cache()
        super(APIKey, self).save(*args, **kwargs)

class Permission(models.Model):
    key = models.ForeignKey('APIKey')
    resource_regex = models.CharField(max_length=256)
    method = models.CharField(choices=zip(METHODS, METHODS), max_length=8)

    def __unicode__(self):
        return u'%s %s %s' % (
            self.key.name,
            self.method,
            self.resource_regex,
        )

    def save(self, *args, **kwargs):
        # invalidate cached permission regexes
        self.key.flush_permissions_cache()
        super(Permission, self).save(*args, **kwargs)

class Limit(models.Model):
    """
    A limit on #calls/time period for each user, session, or api key
    
    Note that limits are on an 'order deny, allow' basis: if you set
    multiple limits that all match a given query, if one of those limits
    is exceeded, the request 420's. So you can set a high blanket .* limit
    and then a much more restrictive per-call limit.
    """
    key = models.ForeignKey('APIKey', null=False)
    resource_regex = models.CharField(max_length=256, blank=False, null=False)
    method = models.CharField(choices=zip(METHODS, METHODS), max_length=8, 
                              null=False, blank=False)
    type = models.CharField(max_length=8, blank=False, null=False,
                            choices=(('session', 'per session'),
                                     ('user', 'per user'),
                                     ('key', 'per key'),
                                     ('ip', 'per ip')))
    period = models.CharField(max_length=8, blank=False, null=False,
                              choices=(('hour', 'per hour'),
                                       ('day', 'per day'),
                                       ('month', 'per month'),
                                       ('year', 'per year'),
                                       ('ever', 'forever')))
    limit = models.IntegerField(null=False)
    
    def __unicode__(self):
        self.key_str = self.key.name
        return ((u"%(limit)d per %(period)s per %(type)s "
                 u"on %(method)s:%(resource_regex)s for %(key_str)s"
                )%self.__dict__)
    
    @property
    def _resource_re(self):
        cache_key = u"limit%d"%self.id
        limit_re = cache.get(cache_key)
        if not limit_re:
            limit_re = re.compile(self.resource_regex)
            cache.set(cache_key, limit_re)
        return limit_re

    def increment_if_matches(self, apikey, request):
        """
        Increment counter if request matches this limit
        
        Returns True if limit is exceeded.
        """
        if ((request.method != self.method)
            or not self._resource_re.match(request.path)):
            return

        if self.type == 'session':
            querydict = {'session_id': request.session.session_key,
                         'key': apikey}
        elif self.type == 'ip':
            if 'REMOTE_ADDR' not in request.META:
                l.warning("Can't limit on IP - proxying server doesn't pass "
                          "REMOTE_ADDR - see wapiti README")
                return False
            querydict = {'ip': request.META['REMOTE_ADDR'],
                         'key': apikey}
        elif self.type == 'user':
            if request.user.is_anonymous():
                return True
            querydict = {'user': request.user.id, 'key': apikey}
        elif self.type == 'key':
            querydict = {'key': apikey}
        try:
            limit_count, created = self.limittracking_set.get_or_create(
                **querydict
            )
        except LimitTracking.MultipleObjectsReturned:
            # because many API requests might come in at the same time,
            # 2 django processes might call get_or_create at the same time,
            # and both will therefore create new objects
            # we take the highest count one, and delete the others
            limit_count = self.limittracking_set.filter(
                **querydict
            ).order_by('-count')[0]
            self.limittracking_set.exclude(id=limit_count.id).delete()

        return limit_count.increment()

class LimitTracking(models.Model):
    key = models.ForeignKey('APIKey', null=False)
    limit = models.ForeignKey("Limit", null=False)
    user = models.ForeignKey(User, null=True, blank=True)
    session_id = models.CharField(max_length=40, blank=True)
    count = models.IntegerField(default=0, null=False)
    ip = models.GenericIPAddressField(blank=True, null=True)
    last_update = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return u'%s out of %s' % (self.count, self.limit)

    def increment(self):
        """Resets counter based on time, or increments it

        Returns True if limit exceeded"""
        if self.limit.period != 'ever':
            now = getattr(dt.datetime.now(), self.limit.period)
            if now != getattr(self.last_update, self.limit.period):
                self.count = 1
                self.save()
                return self.count > self.limit.limit

        if self.count >= self.limit.limit:
            return True
        self.count = F('count') + 1
        self.save()

class LogItem(models.Model):
    """Log all API queries"""
    apikey = models.ForeignKey('APIKey', null=False)
    method = models.CharField(choices=zip(METHODS, METHODS), max_length=8, 
                              null=False, blank=False)
    resource = models.CharField(max_length=256, blank=False, null=False)
    pickled_arguments = models.TextField(blank=True)

    @classmethod
    def log_api_call(self, apikey, request, args):
        self.objects.create(
            apikey=apikey,
            method=request.method,
            resource=request.path,
            pickled_arguments=base64.encodestring(Pickle.dumps(args, 2))
        )

    @property
    def arguments(self):
        """Decode and unpickle the arguments back into python"""
        return Pickle.loads(base64.decodestring(self.pickled_arguments))


