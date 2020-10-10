from spce import CloudEvent, Json

from .source import EventSource


class Http:

    def __init__(self, client, base_url, path = ""):
        self.client = client
        self.base_url = base_url
        self.path = path or "/event"

    def event_source(self, path: str="", *,
                     type="",
                     source="",
                     datacontenttype="application/json",
                     dataschema="",
                     subject="") -> EventSource:
        client = Http(self.client, self.base_url, f'/{path.strip("/")}')
        return EventSource(client,
                           type=type,
                           source=source,
                           datacontenttype=datacontenttype,
                           dataschema=dataschema,
                           subject=subject)

    def post_event(self, event: CloudEvent, path = ""):
        path = path or self.path
        body, headers = self._make_body_headers(event, "json")
        url = f"{self.base_url}{path}"
        return self.client.request("POST", url, headers=headers, body=body)

    @classmethod
    def _make_body_headers(self, event, format):
        if format == "json":
            headers = {
                "content-type": "application/cloudevents+json"
            }
            body = Json.encode(event)
        elif format == "avro":
            headers = {
                "content-type": "application/cloudevents+avro"
            }
            body = Avro.encode(event)
        else:
            raise RuntimeError("_make_headers: %s is not a valid format" % format)

        return body, headers
