from slowapi import Limiter
from slowapi.util import get_remote_address

# Import this in every router that needs rate limiting
limiter = Limiter(key_func=get_remote_address)