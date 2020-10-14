import uuid
from datetime import datetime

from spce import CloudEvent


class EventSource:

    def __init__(self, client, *,
                 type="",
                 source="",
                 datacontenttype="application/json",
                 dataschema="",
                 subject=""
         ):
        self.client = client
        self.type = type
        self.source = source or str(uuid.uuid4())
        self.datacontenttype = datacontenttype
        self.dataschema = dataschema
        self.subject=subject
        self._id_seq = 1

    def post_event(self, *,
              type= "",
              source= "",
              id="",
              subject="",
              time="",
              datacontenttype="application/json",
              dataschema="",
              data=None,
              **attrs) -> CloudEvent:
        type = type or self.type
        source = source or self.source
        id = str(id) if id else str(self._id_seq)
        time = time or datetime.utcnow()
        datacontenttype=datacontenttype or self.datacontenttype
        dataschema=dataschema or self.dataschema

        event = CloudEvent(
            type=type,
            source=source,
            id=id,
            time=time,
            subject=subject,
            data=data,
            datacontenttype=datacontenttype if data else "",
            dataschema=dataschema if data else "",
            **attrs
        )

        # TODO: make this thread-safe
        self._id_seq += 1
        self.client.post_event(event)

        return event



