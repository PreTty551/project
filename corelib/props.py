# -*- coding: utf-8 -*-
import json

from django.conf import settings
from corelib.redis import redis


class PropsMixin(object):
    """
    继承的类需要实现_props_db_key方法
    """

    @property
    def _props_db_key(self):
        raise Exception("%s instance not property '_props_db_key'." % self.__class__)

    def _set_props(self, props):
        redis.hmset(self._props_db_key, props)

    def _get_props(self):
        return redis.hgetall(self._props_db_key)

    get_props = _get_props
    set_props = _set_props

    props = property(_get_props, _set_props)

    def set_props_item(self, key, value):
        # 防止None字符串写入进去
        if value == "None":
            return

        props = self.props
        props[key] = json.dumps(value)
        self.props = props

    def get_props_item(self, key, default=""):
        value = self.props.get(key.encode(encoding="utf-8"))
        if value:
            return json.loads(value.decode())
        return default

    def delete_props_item(self, key):
        redis.hdel(self._props_db_key, key.encode(encoding="utf-8"))

    def incr_props_item(self, key, amount=1):
        redis.hincrby(self._props_db_key, key.encode(encoding="utf-8"), amount)

    def delete(self):
        redis.delete(self._props_db_key)
