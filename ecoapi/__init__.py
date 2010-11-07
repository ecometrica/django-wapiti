import random
import re
import string

from helpers import *

APIKEY_ALLOWABLE_LETTERS = string.letters + string.digits
APIKEY_LENGTH = 32
ID_RE = re.compile('[0-9]+')

RegisteredType = namedtuple('RegisteredType', ('model', ))

registered_types = {}

register_models()

