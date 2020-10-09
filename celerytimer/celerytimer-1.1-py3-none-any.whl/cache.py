import json

import redis


class CacheValue(object):
    """
    批量缓存 key:value

    """

    def __init__(self, host, port, db):
        self.redis_conn = redis.StrictRedis(host=host, port=port, db=db)

    @staticmethod
    def construct_key(key: str, prefix_key: str) -> str:
        """
        构建缓存的key
        :param key: key值
        :param prefix_key: 前缀的key
        """
        if prefix_key:
            key = f"{prefix_key}:{key}"
        else:
            key = f"{key}"
        return key

    def _save_cache_data(self, data: dict, timeout=None, prefix_key=None):
        """lua脚本批量保存key:value
        :param data: 需要保存的数据：{key1:value1,key2:value2,...}
        """

        # 指定过期时间
        timeout_lua_script = """
                    local len = #ARGV
                    local timeout = tonumber(ARGV[len]) --value列表中的最后一个为超时时间 
                    for i,key in ipairs(KEYS) do
                        redis.call("setex",key,timeout,ARGV[i])
                    end
                """
        # 不指定过期时间
        lua_script = """
                            local len = #ARGV
                            for i,key in ipairs(KEYS) do
                                redis.call("set",key,ARGV[i])
                            end
                        """

        cache_keys, cache_values = list(), list()
        for key, value in data.items():
            cache_keys.append(self.construct_key(key, prefix_key))
            cache_values.append(value)
        if timeout:
            cache_values.append(timeout)  # values列表最后一个为过期时间
            lua_obj = self.redis_conn.register_script(timeout_lua_script)
        else:
            lua_obj = self.redis_conn.register_script(lua_script)
        res = lua_obj(keys=cache_keys, args=cache_values)
        return res

    def _get_cache_data(self, data: list, prefix_key=None) -> dict:
        """lua批量获取key:value
        :param data: 缓存的key值列表
        """
        cache_keys = [self.construct_key(key, prefix_key) for key in data]
        lua_script = """
                local values = {}
                for i,key in ipairs(KEYS) do
                    local data = redis.call("get",key)
                    values[i] = data
                end
                return values
        """
        lua_obj = self.redis_conn.register_script(lua_script)
        values = lua_obj(keys=cache_keys)

        key_value_dict = dict()
        for i, value in enumerate(values):
            key = data[i]
            if value is None:
                key_value_dict[key] = ""
            else:
                try:
                    key_value_dict[key] = json.loads(bytes.decode(value))
                except Exception as e:
                    key_value_dict[key] = bytes.decode(value)
        return key_value_dict

    def _del_cache_data(self, data: list, prefix_key=None):
        """lua批量删除key
        :param data: 需要删除的keys列表
        """
        cache_keys = [self.construct_key(key, prefix_key) for key in data]
        lua_script = """
                        for i,key in ipairs(KEYS) do
                            local data = redis.call("del",key)
                        end
                """
        lua_obj = self.redis_conn.register_script(lua_script)
        res = lua_obj(keys=cache_keys)
        return res

    def m_set(self, data: dict, timeout=None, prefix_key=None):
        """批量设置key:value
        :param data: 需要缓存的数据 {key1:value1,key2:value2}
        :param prefix_key: 前缀的key
        :param timeout: 过期时间
        :return
        """
        if not isinstance(data, dict):
            raise Exception("传参类型错误！！！")
        if not data:
            return
        res = self._save_cache_data(data, timeout, prefix_key)

    def m_get(self, keys: list, prefix_key=None) -> dict:
        """批量获取key:value
        :param keys: key列表 [key1,key2,key3]
        :param prefix_key: 前缀的key   组成一个新的key：prefix_key:key
        :return {key1:value1,key2:value2}
        """
        data = self._get_cache_data(keys, prefix_key)
        return data

    def m_del(self, keys: list, prefix_key=None):
        """批量删除key:value
        :param keys: 需要删除的keys列表
        :param prefix_key: 前缀的key
        """
        res = self._del_cache_data(keys, prefix_key)
