import json
import time

# local config helper
try:
    import ISReader.configutil as configutil
except ImportError:
    import configutil
try:
    import ISReader.version as version
except ImportError:
    import version

# python 2 and 3 conversion support
import sys
if (sys.version_info < (2,7,0)):
    sys.stderr.write("You need at least python 2.7.0 to use the ISReader")
    exit(1)
elif (sys.version_info >= (3,0)):
    import http.client as httplib
    from urllib.parse import urlencode
else:
    import httplib
    from urllib import urlencode


class Reader:

    def __init__(self, access_key=None, bucket_key=None, ini_file_location=None, debug_level=0, resource_base='/data'):
        config = configutil.getConfig(ini_file_location)
        print(config)

        self.api_base = config["api_base"]
        self.resource_base = resource_base
        self.debug_level = debug_level
        self.access_key = access_key or config.get('access_key')
        self.bucket_key = bucket_key or config.get('bucket_key')

        if not (self.access_key and self.bucket_key):
            raise Exception('Access key and bucket key required')

        self.console_message("access_key: {accessKey}".format(accessKey=self.access_key))
        self.console_message("bucket_key: {bucketKey}".format(bucketKey=self.bucket_key))
        self.console_message("api_base: {api}".format(api=self.api_base))

    def console_message(self, message, level=1):
        if (self.debug_level >= level):
            print(message)

    def make_request(self, resource, query_params=None, method='GET', retry_attempts=3, wait=0):
        headers = {
            'Accept': 'application/json',
            'User-Agent': 'ISReader v' + version.__version__,
            'X-IS-AccessKey': self.access_key,
            'X-IS-BucketKey': self.bucket_key
        }
        if query_params:
            resource += "?{query_string}".format(query_string=urlencode(query_params))

        def _send(retry_attempts, wait=0):
            conn = None
            response = None
            if (self.api_base.startswith('https://')):
                api_base = self.api_base[8:]
                self.console_message("{method} {resource}: stream api base domain: {domain}".format(method=method, domain=api_base, resource=resource), level=2)
                conn = httplib.HTTPSConnection(api_base, timeout=120)
            else:
                api_base = self.api_base[7:]
                self.console_message("{method} {resource}: stream api base domain: {domain}".format(method=method, domain=api_base, resource=resource), level=2)
                conn = httplib.HTTPConnection(api_base, timeout=120)

            retry_attempts = retry_attempts - 1
            if (retry_attempts < 0):
                if (self.debug_level >= 2):
                    raise Exception("Request failed.. network issue?")
                else:
                    self.console_message("ISReader failed request after a number of attempts.", level=0)
                    return

            try:
                if (wait > 0):
                    self.console_message("ISReader pausing thread for {wait} seconds".format(wait=wait))
                    time.sleep(wait)

                if method == 'GET':
                    conn.request(method, resource, headers=headers)
                else:
                    raise NotImplementedError()
                response = conn.getresponse()
                response_body = response.read()

                if (response.status >= 200 and response.status < 300):
                    self.console_message("ISReader status: " + str(response.status), level=2)
                    self.console_message("ISReader headers: " + str(response.msg), level=2)
                    self.console_message("ISReader body: " + str(response_body), level=3)
                    try:
                        return json.loads(response_body)
                    except Exception as ex:
                        pass
                elif (response.status == 400):
                    try:
                        json_err = json.loads(response_body)
                        if json_err["message"]["error"]["type"]:
                            self.console_message(json_err["message"]["error"]["message"])
                    except Exception as ex:
                        self.console_message("ERROR: Bad Request")
                elif response.status == 401:
                    self.console_message("ERROR: Unauthorized")
                elif response.status == 403:
                    self.console_message("ERROR: Forbidden")
                elif (response.status == 429):
                    if "Retry-After" in response.msg:
                        retry_after = response.msg["Retry-After"]
                        self.console_message("Request limit exceeded, wait {limit} seconds before trying again".format(limit=retry_after))
                        _send(retry_attempts, int(retry_after)+1)
                    else:
                        self.console_message("Request limit exceeded")
                else:
                    self.console_message("ISReader failed on attempt {atmpt} (StatusCode: {sc}; Reason: {r})".format(sc=response.status, r=response.reason, atmpt=retry_attempts))
                    raise Exception("ship exception")
            except Exception as ex:
                if (len(ex.args) > 0 and ex.args[0] == "PAYMENT_REQUIRED"):
                    raise Exception("Either account is capped or an upgrade is required.")

                self.console_message("ISReader exception on attempt {atmpt}.".format(atmpt=retry_attempts))
                if (self.debug_level > 1):
                    raise ex
                else:
                    self.console_message("Exception gobbled: {}".format(str(ex)))

        return _send(retry_attempts, wait)

    def get_latest(self, keys=None):
        resource = self.resource_base + "/v1/events/latest"
        query_params = [('key', k) for k in keys] if keys else None
        return self.make_request(resource, query_params=query_params, wait=0.1)
