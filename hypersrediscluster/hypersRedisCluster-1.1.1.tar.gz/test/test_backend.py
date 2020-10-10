import base64
import datetime
import time
import unittest
from datetime import timedelta
from unittest.mock import patch

from django import VERSION
from django.conf import settings
from django.contrib.sessions.backends.cache import SessionStore as CacheSession
from django.core.cache import cache, caches
from django.test import override_settings
from django.utils import timezone
from django_redis.cache import DJANGO_REDIS_SCAN_ITERSIZE
from django_redis.client import ShardClient, herd
from django_redis.serializers.json import JSONSerializer
from django_redis.serializers.msgpack import MSGPackSerializer


def clearn_up(self, key):
    self.cache.delete(key)
    resFinal = self.cache.get(key)
    self.assertEqual(resFinal, None)


class DjangoRedisCacheTests(unittest.TestCase):
    def setUp(self):
        self.cache = cache
        try:
            self.cache.clear()
        except:
            pass

    def test_setnx(self):
        self.cache.delete("test_key_nx")
        res = self.cache.get("test_key_nx")
        self.assertEqual(res, None)

        res1 = self.cache.set("test_key_nx", 1, nx=True)
        self.assertTrue(res1)
        res2 = self.cache.set("test_key_nx", 2, nx=True)
        self.assertFalse(res2)

        resFinal = self.cache.get("test_key_nx")
        self.assertEqual(resFinal, 1)

        clearn_up(self, "test_key_nx")

    def test_setnx_timeout(self):
        res = self.cache.set("test_key_nx", 1, timeout=2, nx=True)
        self.assertTrue(res)
        time.sleep(3)
        res = self.cache.get("test_key_nx")
        self.assertEqual(res, None)

        self.cache.set("test_key_nx", 1)
        res = self.cache.set("test_key_nx", 2, timeout=2, nx=True)
        self.assertFalse(res)
        resFinal = self.cache.get("test_key_nx")
        self.assertEqual(resFinal, 1)

        clearn_up(self, "test_key_nx")

    def test_unicode_keys(self):
        self.cache.set("ключ", "value")
        res = self.cache.get("ключ")
        self.assertEqual(res, "value")

    def test_save_and_integer(self):
        self.cache.set("test_key", 2)
        res = self.cache.get("test_key", "Foo")
        self.assertIsInstance(res, int)
        self.assertEqual(res, 2)

    def test_save_string(self):
        self.cache.set("test_key", "hello" * 1000)
        res1 = self.cache.get("test_key")
        self.assertIsInstance(res1, str)
        self.assertEqual(res1, "hello" * 1000)

        self.cache.set("test_key", "2")
        res2 = self.cache.get("test_key")
        self.assertIsInstance(res2, str)
        self.assertEqual(res2, "2")

    def test_save_unicode(self):
        self.cache.set("test_key", "heló")
        res = self.cache.get("test_key")

        self.assertIsInstance(res, str)
        self.assertEqual(res, "heló")

    def test_save_dict(self):
        if isinstance(
            self.cache.client._serializer, (JSONSerializer, MSGPackSerializer)
        ):
            now_dt = datetime.datetime.now().isoformat()
        else:
            now_dt = datetime.datetime.now()

        test_dict = {"id": 1, "date": now_dt, "name": "Foo"}

        self.cache.set("test_key", test_dict)
        res = self.cache.get("test_key")

        self.assertIsInstance(res, dict)
        self.assertEqual(res["id"], 1)
        self.assertEqual(res["date"], now_dt)
        self.assertEqual(res["name"], "Foo")

    def test_save_float(self):
        float_value = 3.14159267
        self.cache.set("test_key", float_value)
        res = self.cache.get("test_key")
        self.assertIsInstance(res, float)
        self.assertEqual(res, float_value)

    def test_timeout(self):
        self.cache.set("test_key", 222, timeout=3)
        time.sleep(4)
        res = self.cache.get("test_key")
        self.assertEqual(res, None)

    def test_timeout_0(self):
        self.cache.set("test_key", 222, timeout=0)
        res = self.cache.get("test_key")
        self.assertEqual(res, None)

    def test_timeout_parameter_as_positional_argument(self):
        self.cache.set("test_key", 222, -1)
        res = self.cache.get("test_key")
        self.assertIsNone(res)

        self.cache.set("test_key", 222, 1)
        res1 = self.cache.get("test_key")
        self.assertEqual(res1, 222)

        time.sleep(2)
        res2 = self.cache.get("test_key")
        self.assertEqual(res2, None)

        self.cache.set("test_key", 222, None)
        self.cache.set("test_key", 222, -1, nx=True)
        res = self.cache.get("test_key")
        self.assertEqual(res, 222)

    def test_timeout_negative(self):
        self.cache.set("test_key", 222, timeout=-1)
        res = self.cache.get("test_key")
        self.assertIsNone(res)

        self.cache.set("test_key", 222, timeout=None)
        self.cache.set("test_key", 222, timeout=-1)
        res = self.cache.get("test_key")
        self.assertIsNone(res)

        self.cache.set("test_key", 222, timeout=None)
        self.cache.set("test_key", 222, timeout=-1, nx=True)
        res = self.cache.get("test_key")
        self.assertEqual(res, 222)

    def test_timeout_tiny(self):
        self.cache.set("test_key", 222, timeout=0.00001)
        res = self.cache.get("test_key")
        self.assertIn(res, (None, 222))

    def test_set_add(self):
        self.cache.set("add_key", "Initial value")
        self.cache.add("add_key", "New value")
        res = cache.get("add_key")

        self.assertEqual(res, "Initial value")

    def test_get_many(self):
        self.cache.set("a", 1)
        self.cache.set("b", 2)
        self.cache.set("c", 3)

        res = self.cache.get_many(["a", "b", "c"])
        self.assertEqual(res, {"a": 1, "b": 2, "c": 3})

    def test_get_many_unicode(self):
        self.cache.set("a", "1")
        self.cache.set("b", "2")
        self.cache.set("c", "3")

        res = self.cache.get_many(["a", "b", "c"])
        self.assertEqual(res, {"a": "1", "b": "2", "c": "3"})

    def test_set_many(self):
        self.cache.set_many({"a": 1, "b": 2, "c": 3})
        res = self.cache.get_many(["a", "b", "c"])
        self.assertEqual(res, {"a": 1, "b": 2, "c": 3})

    def test_delete(self):
        self.cache.set_many({"a": 1, "b": 2, "c": 3})
        res = self.cache.delete("a")
        self.assertTrue(bool(res))

        res = self.cache.get_many(["a", "b", "c"])
        self.assertEqual(res, {"b": 2, "c": 3})

        res = self.cache.delete("a")
        self.assertFalse(bool(res))

    def test_delete_many(self):
        self.cache.set_many({"a": 1, "b": 2, "c": 3})
        res = self.cache.delete_many(["a", "b"])
        self.assertTrue(bool(res))

        res = self.cache.get_many(["a", "b", "c"])
        self.assertEqual(res, {"c": 3})

        res = self.cache.delete_many(["a", "b"])
        self.assertFalse(bool(res))

    def test_delete_many_generator(self):
        self.cache.set_many({"a": 1, "b": 2, "c": 3})
        res = self.cache.delete_many(key for key in ["a", "b"])
        self.assertTrue(bool(res))

        res = self.cache.get_many(["a", "b", "c"])
        self.assertEqual(res, {"c": 3})

        res = self.cache.delete_many(["a", "b"])
        self.assertFalse(bool(res))

    def test_delete_many_empty_generator(self):
        res = self.cache.delete_many(key for key in [])
        self.assertFalse(bool(res))

    def test_incr(self):
        if isinstance(self.cache.client, herd.HerdClient):
            self.skipTest("HerdClient doesn't support incr")

        self.cache.set("num", 1)

        self.cache.incr("num")
        res = self.cache.get("num")
        self.assertEqual(res, 2)

        self.cache.incr("num", 10)
        res = self.cache.get("num")
        self.assertEqual(res, 12)

        self.cache.set("num", 9223372036854775807)

        self.cache.incr("num")
        res = self.cache.get("num")
        self.assertEqual(res, 9223372036854775808)

        self.cache.incr("num", 2)
        res = self.cache.get("num")
        self.assertEqual(res, 9223372036854775810)

        self.cache.set("num", int(3))

        self.cache.incr("num", 2)
        res = self.cache.get("num")
        self.assertEqual(res, 5)

    def test_incr_error(self):
        if isinstance(self.cache.client, herd.HerdClient):
            self.skipTest("HerdClient doesn't support incr")

        with self.assertRaises(ValueError):
            self.cache.incr("numnum")

    def test_incr_ignore_check(self):
        if isinstance(self.cache.client, ShardClient):
            self.skipTest(
                "ShardClient doesn't support argument ignore_key_check to incr"
            )
        if isinstance(self.cache.client, herd.HerdClient):
            self.skipTest("HerdClient doesn't support incr")

        self.cache.incr("num", ignore_key_check=True)
        res = self.cache.get("num")
        self.assertEqual(res, 1)
        self.cache.delete("num")

        self.cache.incr("num", 10, ignore_key_check=True)
        res = self.cache.get("num")
        self.assertEqual(res, 10)
        self.cache.delete("num")

        self.cache.set("num", 9223372036854775807)

        self.cache.incr("num", ignore_key_check=True)
        res = self.cache.get("num")
        self.assertEqual(res, 9223372036854775808)

        self.cache.incr("num", 2, ignore_key_check=True)
        res = self.cache.get("num")
        self.assertEqual(res, 9223372036854775810)

        self.cache.set("num", int(3))

        self.cache.incr("num", 2, ignore_key_check=True)
        res = self.cache.get("num")
        self.assertEqual(res, 5)

    def test_get_set_bool(self):
        self.cache.set("bool", True)
        res = self.cache.get("bool")

        self.assertIsInstance(res, bool)
        self.assertEqual(res, True)

        self.cache.set("bool", False)
        res = self.cache.get("bool")

        self.assertIsInstance(res, bool)
        self.assertEqual(res, False)

    def test_decr(self):
        if isinstance(self.cache.client, herd.HerdClient):
            self.skipTest("HerdClient doesn't support decr")

        self.cache.set("num", 20)

        self.cache.decr("num")
        res = self.cache.get("num")
        self.assertEqual(res, 19)

        self.cache.decr("num", 20)
        res = self.cache.get("num")
        self.assertEqual(res, -1)

        self.cache.decr("num", int(2))
        res = self.cache.get("num")
        self.assertEqual(res, -3)

        self.cache.set("num", int(20))

        self.cache.decr("num")
        res = self.cache.get("num")
        self.assertEqual(res, 19)

        # max 64 bit signed int + 1
        self.cache.set("num", 9223372036854775808)

        self.cache.decr("num")
        res = self.cache.get("num")
        self.assertEqual(res, 9223372036854775807)

        self.cache.decr("num", 2)
        res = self.cache.get("num")
        self.assertEqual(res, 9223372036854775805)

    def test_version(self):
        self.cache.set("keytest", 2, version=2)
        res = self.cache.get("keytest")
        self.assertEqual(res, None)

        res = self.cache.get("keytest", version=2)
        self.assertEqual(res, 2)

    def test_incr_version(self):
        self.cache.set("keytest", 2)
        self.cache.incr_version("keytest")

        res = self.cache.get("keytest")
        self.assertEqual(res, None)

        res = self.cache.get("keytest", version=2)
        self.assertEqual(res, 2)

    def test_delete_pattern(self):
        for key in ["foo-aa", "foo-ab", "foo-bb", "foo-bc"]:
            self.cache.set(key, "foo")

        res = self.cache.delete_pattern("*foo-a*")
        self.assertTrue(bool(res))

        keys = self.cache.keys("foo*")
        self.assertEqual(set(keys), {"foo-bb", "foo-bc"})

        res = self.cache.delete_pattern("*foo-a*")
        self.assertFalse(bool(res))

    def test_close(self):
        cache = caches["default"]
        cache.set("f", "1")
        cache.close()

    def test_ttl(self):
        cache = caches["default"]

        # Test ttl
        cache.set("foo", "bar", 10)
        ttl = cache.ttl("foo")

        if isinstance(cache.client, herd.HerdClient):
            self.assertAlmostEqual(ttl, 12)
        else:
            self.assertAlmostEqual(ttl, 10)

        # Test ttl None
        cache.set("foo", "foo", timeout=None)
        ttl = cache.ttl("foo")
        self.assertEqual(ttl, None)

        # Test ttl with expired key
        cache.set("foo", "foo", timeout=-1)
        ttl = cache.ttl("foo")
        self.assertEqual(ttl, 0)

        # Test ttl with not existent key
        ttl = cache.ttl("not-existent-key")
        self.assertEqual(ttl, 0)

    def test_persist(self):
        self.cache.set("foo", "bar", timeout=20)
        self.cache.persist("foo")

        ttl = self.cache.ttl("foo")
        self.assertIsNone(ttl)

    def test_expire(self):
        self.cache.set("foo", "bar", timeout=None)
        self.cache.expire("foo", 20)
        ttl = self.cache.ttl("foo")
        self.assertAlmostEqual(ttl, 20)

    def test_lock(self):
        lock = self.cache.lock("foobar")
        lock.acquire(blocking=True)

        self.assertTrue(self.cache.has_key("foobar"))
        lock.release()
        self.assertFalse(self.cache.has_key("foobar"))

    def test_iter_keys(self):
        cache = caches["default"]
        if isinstance(cache.client, ShardClient):
            self.skipTest("ShardClient doesn't support iter_keys")

        cache.set("foo1", 1)
        cache.set("foo2", 1)
        cache.set("foo3", 1)

        # Test simple result
        result = set(cache.iter_keys("foo*"))
        self.assertEqual(result, {"foo1", "foo2", "foo3"})

        # Test limited result
        result = list(cache.iter_keys("foo*", itersize=2))
        self.assertEqual(len(result), 3)

        # Test generator object
        result = cache.iter_keys("foo*")
        self.assertNotEqual(next(result), None)

    @patch("django_redis.cache.RedisCache.client")
    def test_delete_pattern_with_custom_count(self, client_mock):
        for key in ["foo-aa", "foo-ab", "foo-bb", "foo-bc"]:
            self.cache.set(key, "foo")

        self.cache.delete_pattern("*foo-a*", itersize=2)

        client_mock.delete_pattern.assert_called_once_with(
            "*foo-a*", itersize=2
        )

    @patch("django_redis.cache.RedisCache.client")
    def test_delete_pattern_with_settings_default_scan_count(
        self, client_mock
    ):
        for key in ["foo-aa", "foo-ab", "foo-bb", "foo-bc"]:
            self.cache.set(key, "foo")
        expected_count = DJANGO_REDIS_SCAN_ITERSIZE

        self.cache.delete_pattern("*foo-a*")

        client_mock.delete_pattern.assert_called_once_with(
            "*foo-a*", itersize=expected_count
        )

    def test_touch_zero_timeout(self):
        self.cache.set("test_key", 222, timeout=10)
        status = self.cache.touch("test_key", 0)
        self.assertEqual(status, True)

        res = self.cache.get("test_key")
        self.assertEqual(res, None)

    def test_touch_positive_timeout(self):
        self.cache.set("test_key", 222, timeout=10)

        self.assertEqual(self.cache.touch("test_key", 2), True)
        self.assertEqual(self.cache.get("test_key"), 222)
        time.sleep(3)
        self.assertEqual(self.cache.get("test_key"), None)

    def test_touch_negative_timeout(self):
        self.cache.set("test_key", 222, timeout=10)

        self.assertEqual(self.cache.touch("test_key", -1), True)
        res = self.cache.get("test_key")
        self.assertEqual(res, None)

    def test_touch_missed_key(self):
        self.assertEqual(self.cache.touch("test_key", -1), False)


class SessionTestCase(unittest.TestCase):
    backend = CacheSession

    def setUp(self):
        self.session = self.backend()

    def tearDown(self):
        self.session.delete()

    def test_new_session(self):
        self.assertIs(self.session.modified, False)
        self.assertIs(self.session.accessed, False)

    def test_get_empty(self):
        self.assertIsNone(self.session.get("cat"))

    def test_store(self):
        self.session["cat"] = "dog"
        self.assertIs(self.session.modified, True)
        self.assertEqual(self.session.pop("cat"), "dog")

    def test_pop(self):
        self.session["some key"] = "exists"
        # Need to reset these to pretend we haven't accessed it:
        self.accessed = False
        self.modified = False

        self.assertEqual(self.session.pop("some key"), "exists")
        self.assertIs(self.session.accessed, True)
        self.assertIs(self.session.modified, True)
        self.assertIsNone(self.session.get("some key"))

    def test_pop_default(self):
        self.assertEqual(
            self.session.pop("some key", "does not exist"), "does not exist"
        )
        self.assertIs(self.session.accessed, True)
        self.assertIs(self.session.modified, False)

    def test_pop_default_named_argument(self):
        self.assertEqual(
            self.session.pop("some key", default="does not exist"),
            "does not exist",
        )
        self.assertIs(self.session.accessed, True)
        self.assertIs(self.session.modified, False)

    def test_pop_no_default_keyerror_raised(self):
        with self.assertRaises(KeyError):
            self.session.pop("some key")

    def test_setdefault(self):
        self.assertEqual(self.session.setdefault("foo", "bar"), "bar")
        self.assertEqual(self.session.setdefault("foo", "baz"), "bar")
        self.assertIs(self.session.accessed, True)
        self.assertIs(self.session.modified, True)

    def test_update(self):
        self.session.update({"update key": 1})
        self.assertIs(self.session.accessed, True)
        self.assertIs(self.session.modified, True)
        self.assertEqual(self.session.get("update key"), 1)

    def test_has_key(self):
        self.session["some key"] = 1
        self.session.modified = False
        self.session.accessed = False
        self.assertIn("some key", self.session)
        self.assertIs(self.session.accessed, True)
        self.assertIs(self.session.modified, False)

    def test_values(self):
        self.assertEqual(list(self.session.values()), [])
        self.assertIs(self.session.accessed, True)
        self.session["some key"] = 1
        self.session.modified = False
        self.session.accessed = False
        self.assertEqual(list(self.session.values()), [1])
        self.assertIs(self.session.accessed, True)
        self.assertIs(self.session.modified, False)

    def test_keys(self):
        self.session["x"] = 1
        self.session.modified = False
        self.session.accessed = False
        self.assertEqual(list(self.session.keys()), ["x"])
        self.assertIs(self.session.accessed, True)
        self.assertIs(self.session.modified, False)

    def test_items(self):
        self.session["x"] = 1
        self.session.modified = False
        self.session.accessed = False
        self.assertEqual(list(self.session.items()), [("x", 1)])
        self.assertIs(self.session.accessed, True)
        self.assertIs(self.session.modified, False)

    def test_clear(self):
        self.session["x"] = 1
        self.session.modified = False
        self.session.accessed = False
        self.assertEqual(list(self.session.items()), [("x", 1)])
        self.session.clear()
        self.assertEqual(list(self.session.items()), [])
        self.assertIs(self.session.accessed, True)
        self.assertIs(self.session.modified, True)

    def test_save(self):
        self.session.save()
        self.assertIs(self.session.exists(self.session.session_key), True)

    def test_delete(self):
        self.session.save()
        self.session.delete(self.session.session_key)
        self.assertIs(self.session.exists(self.session.session_key), False)

    def test_flush(self):
        self.session["foo"] = "bar"
        self.session.save()
        prev_key = self.session.session_key
        self.session.flush()
        self.assertIs(self.session.exists(prev_key), False)
        self.assertNotEqual(self.session.session_key, prev_key)
        self.assertIsNone(self.session.session_key)
        self.assertIs(self.session.modified, True)
        self.assertIs(self.session.accessed, True)

    def test_cycle(self):
        self.session["a"], self.session["b"] = "c", "d"
        self.session.save()
        prev_key = self.session.session_key
        prev_data = list(self.session.items())
        self.session.cycle_key()
        self.assertIs(self.session.exists(prev_key), False)
        self.assertNotEqual(self.session.session_key, prev_key)
        self.assertEqual(list(self.session.items()), prev_data)

    def test_cycle_with_no_session_cache(self):
        self.session["a"], self.session["b"] = "c", "d"
        self.session.save()
        prev_data = self.session.items()
        self.session = self.backend(self.session.session_key)
        self.assertIs(hasattr(self.session, "_session_cache"), False)
        self.session.cycle_key()
        self.assertCountEqual(self.session.items(), prev_data)

    def test_save_doesnt_clear_data(self):
        self.session["a"] = "b"
        self.session.save()
        self.assertEqual(self.session["a"], "b")

    def test_invalid_key(self):
        # Submitting an invalid session key (either by guessing, or if the db has
        # removed the key) results in a new key being generated.
        try:
            session = self.backend("1")
            session.save()
            self.assertNotEqual(session.session_key, "1")
            self.assertIsNone(session.get("cat"))
            session.delete()
        finally:
            # Some backends leave a stale cache entry for the invalid
            # session key; make sure that entry is manually deleted
            session.delete("1")

    def test_session_key_empty_string_invalid(self):
        """Falsey values (Such as an empty string) are rejected."""
        self.session._session_key = ""
        self.assertIsNone(self.session.session_key)

    def test_session_key_too_short_invalid(self):
        """Strings shorter than 8 characters are rejected."""
        self.session._session_key = "1234567"
        self.assertIsNone(self.session.session_key)

    def test_session_key_valid_string_saved(self):
        """Strings of length 8 and up are accepted and stored."""
        self.session._session_key = "12345678"
        self.assertEqual(self.session.session_key, "12345678")

    def test_session_key_is_read_only(self):
        def set_session_key(session):
            session.session_key = session._get_new_session_key()

        with self.assertRaises(AttributeError):
            set_session_key(self.session)

    # Custom session expiry
    def test_default_expiry(self):
        # A normal session has a max age equal to settings
        self.assertEqual(
            self.session.get_expiry_age(), settings.SESSION_COOKIE_AGE
        )

        # So does a custom session with an idle expiration time of 0 (but it'll
        # expire at browser close)
        self.session.set_expiry(0)
        self.assertEqual(
            self.session.get_expiry_age(), settings.SESSION_COOKIE_AGE
        )

    def test_custom_expiry_seconds(self):
        modification = timezone.now()

        self.session.set_expiry(10)

        date = self.session.get_expiry_date(modification=modification)
        self.assertEqual(date, modification + timedelta(seconds=10))

        age = self.session.get_expiry_age(modification=modification)
        self.assertEqual(age, 10)

    def test_custom_expiry_timedelta(self):
        modification = timezone.now()

        # Mock timezone.now, because set_expiry calls it on this code path.
        original_now = timezone.now
        try:
            timezone.now = lambda: modification
            self.session.set_expiry(timedelta(seconds=10))
        finally:
            timezone.now = original_now

        date = self.session.get_expiry_date(modification=modification)
        self.assertEqual(date, modification + timedelta(seconds=10))

        age = self.session.get_expiry_age(modification=modification)
        self.assertEqual(age, 10)

    def test_custom_expiry_datetime(self):
        modification = timezone.now()

        self.session.set_expiry(modification + timedelta(seconds=10))

        date = self.session.get_expiry_date(modification=modification)
        self.assertEqual(date, modification + timedelta(seconds=10))

        age = self.session.get_expiry_age(modification=modification)
        self.assertEqual(age, 10)

    def test_custom_expiry_reset(self):
        self.session.set_expiry(None)
        self.session.set_expiry(10)
        self.session.set_expiry(None)
        self.assertEqual(
            self.session.get_expiry_age(), settings.SESSION_COOKIE_AGE
        )

    def test_get_expire_at_browser_close(self):
        # Tests get_expire_at_browser_close with different settings and different
        # set_expiry calls
        with override_settings(SESSION_EXPIRE_AT_BROWSER_CLOSE=False):
            self.session.set_expiry(10)
            self.assertIs(self.session.get_expire_at_browser_close(), False)

            self.session.set_expiry(0)
            self.assertIs(self.session.get_expire_at_browser_close(), True)

            self.session.set_expiry(None)
            self.assertIs(self.session.get_expire_at_browser_close(), False)

        with override_settings(SESSION_EXPIRE_AT_BROWSER_CLOSE=True):
            self.session.set_expiry(10)
            self.assertIs(self.session.get_expire_at_browser_close(), False)

            self.session.set_expiry(0)
            self.assertIs(self.session.get_expire_at_browser_close(), True)

            self.session.set_expiry(None)
            self.assertIs(self.session.get_expire_at_browser_close(), True)

    def test_decode(self):
        # Ensure we can decode what we encode
        data = {"a test key": "a test value"}
        encoded = self.session.encode(data)
        self.assertEqual(self.session.decode(encoded), data)

    def test_decode_failure_logged_to_security(self):
        bad_encode = base64.b64encode(b"flaskdj:alkdjf").decode("ascii")
        with self.assertLogs(
            "django.security.SuspiciousSession", "WARNING"
        ) as cm:
            self.assertEqual({}, self.session.decode(bad_encode))
        # The failed decode is logged.
        self.assertIn("corrupted", cm.output[0])

    def test_actual_expiry(self):
        # this doesn't work with JSONSerializer (serializing timedelta)
        with override_settings(
            SESSION_SERIALIZER="django.contrib.sessions.serializers.PickleSerializer"
        ):
            self.session = (
                self.backend()
            )  # reinitialize after overriding settings

            # Regression test for #19200
            old_session_key = None
            new_session_key = None
            try:
                self.session["foo"] = "bar"
                self.session.set_expiry(-timedelta(seconds=10))
                self.session.save()
                old_session_key = self.session.session_key
                # With an expiry date in the past, the session expires instantly.
                new_session = self.backend(self.session.session_key)
                new_session_key = new_session.session_key
                self.assertNotIn("foo", new_session)
            finally:
                self.session.delete(old_session_key)
                self.session.delete(new_session_key)

    @unittest.skipIf(VERSION < (2, 0), "Requires Django 2.0+")
    def test_session_load_does_not_create_record(self):
        """
        Loading an unknown session key does not create a session record.
        Creating session records on load is a DOS vulnerability.
        """
        session = self.backend("someunknownkey")
        session.load()

        self.assertIsNone(session.session_key)
        self.assertIs(session.exists(session.session_key), False)
        # provided unknown key was cycled, not reused
        self.assertNotEqual(session.session_key, "someunknownkey")

    def test_session_save_does_not_resurrect_session_logged_out_in_other_context(
        self
    ):
        """
        Sessions shouldn't be resurrected by a concurrent request.
        """
        from django.contrib.sessions.backends.base import UpdateError

        # Create new session.
        s1 = self.backend()
        s1["test_data"] = "value1"
        s1.save(must_create=True)

        # Logout in another context.
        s2 = self.backend(s1.session_key)
        s2.delete()

        # Modify session in first context.
        s1["test_data"] = "value2"
        with self.assertRaises(UpdateError):
            # This should throw an exception as the session is deleted, not
            # resurrect the session.
            s1.save()

        self.assertEqual(s1.load(), {})
