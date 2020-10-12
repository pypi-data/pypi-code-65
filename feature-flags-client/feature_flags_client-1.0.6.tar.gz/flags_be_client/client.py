import os
import json
import fnmatch
import requests
import socket
import time
import functools
from datetime import datetime, timedelta


environment = os.environ.get("ENVIRONMENT", "dev")
STATSD_HOST = os.environ.get("STATSD_HOST", "localhost")
STATSD_PORT = int(os.environ.get("STATSD_PORT", "8125"))
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


def push_metrics(flag_name, identifier, gated):
    identifier = identifier or "empty"
    gated = 1 if gated else 0
    message = f"feature_flags.[flag_name={flag_name},identifier={identifier},environment={environment}]gated:{gated}|c"
    sock.sendto(message.encode("utf-8"), (STATSD_HOST, STATSD_PORT))


def push_duration(duration_ms):
    message = f"feature_flags.[environment={environment}]duration:{duration_ms}|ms"
    sock.sendto(message.encode("utf-8"), (STATSD_HOST, STATSD_PORT))


def timed_cache(**timedelta_kwargs):
    def _wrapper(f):
        update_delta = timedelta(**timedelta_kwargs)
        next_update = datetime.utcnow() + update_delta
        # Apply @lru_cache to f with no cache size limit
        f = functools.lru_cache(None)(f)

        @functools.wraps(f)
        def _wrapped(*args, **kwargs):
            nonlocal next_update
            now = datetime.utcnow()
            if now >= next_update:
                f.cache_clear()
                next_update = now + update_delta
            return f(*args, **kwargs)

        return _wrapped

    return _wrapper


class FeatureFlagClient:

    # bucket and folder names
    FF_BUCKET_NAME = os.environ.get("FF_BUCKET_NAME", "stitch-feature-flags")
    FF_PRIVATE = os.environ.get("FF_PRIVATE", "feature-flags-private")
    FF_PUBLIC = os.environ.get("FF_PUBLIC", "feature-flags")

    @timed_cache(seconds=60)
    def get_flag_file_content(self, bucket_path):
        response = requests.get(
            f"https://stitch-feature-flags.s3.eu-central-1.amazonaws.com/{bucket_path}/{environment}.json"
        )
        flags_file_content = response.content.decode("utf-8")
        return json.loads(flags_file_content)

    def check_is_visible(self, flag, identifier):
        if not flag["active"]:
            return False

        is_whitelisted = any(
            fnmatch.fnmatch(identifier, pattern) for pattern in flag["whitelist"]
        )
        is_blacklisted = any(
            fnmatch.fnmatch(identifier, pattern) for pattern in flag["blacklist"]
        )

        return is_whitelisted and not is_blacklisted

    def is_enabled(self, flag_name, identifier=""):
        begin = time.time()
        try:
            private_flags_list = self.get_flag_file_content(bucket_path=self.FF_PRIVATE)
            public_flags_list = self.get_flag_file_content(bucket_path=self.FF_PUBLIC)

            flags_list = private_flags_list + public_flags_list

            for flag in flags_list:
                if flag["name"] == flag_name:
                    retval = self.check_is_visible(flag, identifier)
                    push_metrics(flag_name, identifier, retval)
                    return retval
        except Exception:  # pylint: disable=broad-except
            # maybe log the error here at some point?
            pass
        finally:
            end = time.time()
            # duration in milliseconds
            push_duration(int((end - begin) * 1000))
