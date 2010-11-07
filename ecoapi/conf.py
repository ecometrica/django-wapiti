import string
import re


APIKEY_ALLOWABLE_LETTERS = string.letters + string.digits
APIKEY_LENGTH = 32
ID_RE = re.compile('[0-9]+')

