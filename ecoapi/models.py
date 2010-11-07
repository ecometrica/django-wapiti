import random
import re

from django.core.cache import cache
from django.db import models

from ecoapi.conf import APIKEY_ALLOWABLE_LETTERS, APIKEY_LENGTH

METHODS = ('GET', 'POST', 'PUT', 'DELETE')

def new_apikey():
    return ''.join(random.sample(APIKEY_ALLOWABLE_LETTERS, APIKEY_LENGTH))

class APIKey(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField()
    key = models.CharField(max_length=32, default=new_apikey)
    active = models.BooleanField(default=True)
    
    def __unicode__(self):
        return u'%s (%s)'%(self.name, 'act' if self.active else 'dis')

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

