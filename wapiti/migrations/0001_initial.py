# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings
import wapiti.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='APIKey',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('slug', models.SlugField()),
                ('key', models.CharField(default=wapiti.models.new_apikey, max_length=32)),
                ('active', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='Limit',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('resource_regex', models.CharField(max_length=256)),
                ('method', models.CharField(max_length=8, choices=[(b'GET', b'GET'), (b'POST', b'POST'), (b'PUT', b'PUT'), (b'DELETE', b'DELETE')])),
                ('type', models.CharField(max_length=8, choices=[(b'session', b'per session'), (b'user', b'per user'), (b'key', b'per key'), (b'ip', b'per ip')])),
                ('period', models.CharField(max_length=8, choices=[(b'hour', b'per hour'), (b'day', b'per day'), (b'month', b'per month'), (b'year', b'per year'), (b'ever', b'forever')])),
                ('limit', models.IntegerField()),
                ('key', models.ForeignKey(to='wapiti.APIKey')),
            ],
        ),
        migrations.CreateModel(
            name='LimitTracking',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('session_id', models.CharField(max_length=40, blank=True)),
                ('count', models.IntegerField(default=0)),
                ('ip', models.IPAddressField(null=True, blank=True)),
                ('last_update', models.DateTimeField(auto_now=True)),
                ('key', models.ForeignKey(to='wapiti.APIKey')),
                ('limit', models.ForeignKey(to='wapiti.Limit')),
                ('user', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='LogItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('method', models.CharField(max_length=8, choices=[(b'GET', b'GET'), (b'POST', b'POST'), (b'PUT', b'PUT'), (b'DELETE', b'DELETE')])),
                ('resource', models.CharField(max_length=256)),
                ('pickled_arguments', models.TextField(blank=True)),
                ('apikey', models.ForeignKey(to='wapiti.APIKey')),
            ],
        ),
        migrations.CreateModel(
            name='Permission',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('resource_regex', models.CharField(max_length=256)),
                ('method', models.CharField(max_length=8, choices=[(b'GET', b'GET'), (b'POST', b'POST'), (b'PUT', b'PUT'), (b'DELETE', b'DELETE')])),
                ('key', models.ForeignKey(to='wapiti.APIKey')),
            ],
        ),
    ]
