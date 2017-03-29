# from django.core.cache import cache as redis
from django_redis import get_redis_connection
redis = get_redis_connection("default")
