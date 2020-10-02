class Configuration():
    def __init__(self, settings):
        self._env = settings.get('env')
        self._site = settings.get('site')
        self._service_name = settings.get('service_name')
        self._enable = settings.get('enable')
        self._url = settings.get('url')
        self._timeout = settings.get('timeout')
        self._max_payload_size = settings.get('max_payload_size')

        self._ignore_url = ['/']