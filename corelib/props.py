# -*- coding: utf-8 -*-
import json

import redis as redis_py

from django.conf import settings


redis_ip = settings.REDIS_CONFIG['default']['HOST']
redis_port = settings.REDIS_CONFIG['default']['PORT']
redis_db = settings.REDIS_CONFIG['default']['DB']

if settings.TESTING:
    redis_db = 1

pool = redis_py.ConnectionPool(host=redis_ip, port=redis_port, db=redis_db)
saydb = redis_py.Redis(connection_pool=pool)



class PropsMixin(object):
    """
    继承的类需要实现_props_db_key方法
    """

    @property
    def _props_db_key(self):
        raise Exception("%s instance not property '_props_db_key'." % self.__class__)

    def _set_props(self, props):
        saydb.hmset(self._props_db_key, props)

    def _get_props(self):
        return saydb.hgetall(self._props_db_key)

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
        value = self.props.get(key)
        if value:
            return json.loads(value)
        return default

    def delete_props_item(self, key):
        saydb.hdel(self._props_db_key, key)

    def incr_props_item(self, key, amount=1):
        saydb.hincrby(self._props_db_key, key, amount)

    def delete(self):
        saydb.delete(self._props_db_key)
