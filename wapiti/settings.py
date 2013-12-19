# Copyright (c) Ecometrica. All rights reserved.
# Distributed under the BSD license. See LICENSE for details.

from django.conf import settings

WAPITI_MAX_SLICE_SIZE = getattr(settings, 'WAPITI_MAX_SLICE_SIZE', 100)

