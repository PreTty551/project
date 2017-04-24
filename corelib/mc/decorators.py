import inspect
import pickle
from django.http import HttpResponseNotFound

from functools import wraps
from .format import format
from .empty import Empty


def cache(key, redis, expire=None):
    def deco(func):
        arg_names, varargs, varkw, defaults = inspect.getargspec(func)
        args = dict(zip(arg_names[-len(defaults):], defaults)) if defaults else {}
        gen_key = gen_key_factory(key, arg_names, defaults)

        if varargs or varkw:
            raise Exception("do not support varargs")

        @wraps(func)
        def _(*args, **kwargs):
            key, _ = gen_key(*args, **kwargs)
            if not key:
                return func(*args, **kwargs)

            value = redis.get(key)
            if value is None:
                value = func(*args, **kwargs)
                if value is not None:
                    redis.set(key, pickle.dumps(value), expire)
            else:
                value = pickle.loads(value)

            if isinstance(value, Empty):
                value = None

            return value
        _.original_function = func
        return _
    return deco


def hlcache(key, redis):
    def deco(func):
        arg_names, varargs, varkw, defaults = inspect.getargspec(func)
        args = dict(zip(arg_names[-len(defaults):], defaults)) if defaults else {}
        gen_key = gen_key_factory(key, arg_names, defaults)
        if varargs or varkw:
            raise Exception("do not support varargs")

        @wraps(func)
        def _(*args, **kwargs):
            key, _ = gen_key(*args, **kwargs)
            if not key:
                return func(*args, **kwargs)

            values = redis.hkeys(key)
            if not values:
                values = func(*args, **kwargs)
                if values:
                    r = {}
                    for v in values:
                        r[v] = 1
                    redis.hmset(key, r)
            else:
                _ll = []
                for v in values:
                    if v.isdigit():
                        _ll.append(int(v))
                    else:
                        _ll.append(v)
                values = _ll
            if isinstance(values, Empty):
                values = []

            return values
        _.original_function = func
        return _
    return deco


def gen_key_factory(key_pattern, arg_names, defaults):
    args = dict(zip(arg_names[-len(defaults):], defaults)) if defaults else {}
    if callable(key_pattern):
        names = inspect.getargspec(key_pattern)[0]

    def gen_key(*a, **kw):
        aa = args.copy()
        aa.update(zip(arg_names, a))
        aa.update(kw)
        if callable(key_pattern):
            key = key_pattern(*[aa[n] for n in names])
        else:
            key = format(key_pattern, *[aa[n] for n in arg_names], **aa)
        return key and key.replace(' ', '_'), aa
    return gen_key


def create_decorators(redis):
    # 因为cache的调用有太多对expire参数的非关键字调用，因此没法用partial方式生成函数

    def _cache(key_pattern, expire=None, redis=redis):
        return cache(key_pattern, redis, expire=expire)

    def _hlcache(key_pattern, edis=redis):
        return hlcache(key_pattern, redis)

    return dict(cache=_cache, hlcache=_hlcache)
