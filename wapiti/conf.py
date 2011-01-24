# Copyright (c) Ecometrica. All rights reserved.
# Distributed under the BSD license. See LICENSE for details.
import string
import re


APIKEY_ALLOWABLE_LETTERS = string.letters + string.digits
APIKEY_LENGTH = 32
ANONYMOUS_API_KEY = 'ANONYMOUS'
ID_RE = re.compile('[0-9]+')

