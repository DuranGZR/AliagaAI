"""Rate limiter instance — ayrı modülde circular import'u önler."""
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
