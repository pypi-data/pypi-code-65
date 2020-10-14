import json
from typing import Union, Callable

from nats.aio.client import Client as NATS
from nats.aio.client import Subscription as NATSSubscription
from stan.aio.client import Client as STAN
from stan.aio.client import Subscription as STANSubscription

from pydantic import BaseModel

from .models import ReplyMessage


class PublisherMixin:

    client: Union[NATS, STAN]

    async def publish(self, subject: str, data: bytes):
        """Publish bytes to a subject.

        Arguments:
            subject: The subject (channel) to publish to.
            data: The content of the message to publish.
        """
        return await self.client.publish(subject, data)

    async def publish_str(self, subject: str, data: str, encoding: str = "utf-8"):
        """Publish a string to a channel

        Arguments:
            subject: The subject (channel) to publish to.
            data: A string to send as message content.
            encoding: Encoding to use when converting string to bytes.
        """
        return await self.publish(subject, bytes(data, encoding))

    async def publish_json(
        self, subject: str, data: Union[dict, list], to_json: Callable = json.dumps
    ):
        """Publish JSON serializable object.

        Arguments:
            subject: The subject (channel) to publish to.
            data: Any JSON serializable object to send as message content.
        """
        json_str = to_json(data)
        return await self.publish_str(subject, json_str)

    async def publish_model(self, subject: str, model: BaseModel):
        """Publish a pydantic model.

        Arguments:
            subject: The subject (channel) to publish to.
            data: Any instance of a class that inherits `pydantic.BaseModel`
        """
        return await self.publish_str(subject, model.json())

    async def request(self, subject, data: bytes, timeout: int = 10) -> ReplyMessage:
        """Publish bytes to subject and expect a response."""
        try:
            reply_msg = await self.client.request(subject, data, timeout=timeout)
        except AttributeError:
            raise NotImplementedError(
                "Request/Reply pattern is not implemented in NATS Streaming."
            )
        return ReplyMessage.parse_raw(reply_msg.data)

    async def request_str(
        self, subject, data: str, timeout: int = 10, encoding: str = "utf-8"
    ) -> ReplyMessage:
        return await self.request(subject, bytes(data, encoding), timeout=timeout)

    async def request_json(
        self,
        subject,
        data: Union[dict, list],
        to_json: Callable = json.dumps,
        timeout: int = 10,
    ) -> ReplyMessage:
        json_str = to_json(data)
        return await self.request_str(subject, json_str, timeout=timeout)

    async def request_model(
        self, subject, model: BaseModel, timeout: int = 10
    ) -> ReplyMessage:
        json_str = model.json()
        return await self.request_str(subject, json_str, timeout=timeout)
