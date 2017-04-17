from corelib.redis import redis
from .decorators import create_decorators
globals().update(create_decorators(redis))
