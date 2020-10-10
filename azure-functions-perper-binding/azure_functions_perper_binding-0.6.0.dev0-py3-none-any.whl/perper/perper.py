import json
import typing

from azure.functions import meta
from pyignite import Client

from ._perper import AbstractPerperCache


class PerperCache(AbstractPerperCache):
    """A concrete implementation of PerperCache type."""

    def __init__(self, *,
                 stream_name: str) -> None:
        self.__stream_name = stream_name

    def get_data(self) -> list:
        client = Client()
        client.connect('localhost', 10800)

        streams_cache = client.get_or_create_cache(json.loads(self.__stream_name)['Stream'])
        stream = streams_cache.scan()
        return list(stream)

    def __repr__(self) -> str:
        return (
            f'<azure.PerperCache '
            f'at 0x{id(self):0x}>'
        )


class PerperStreamConverter(meta.InConverter,
                            binding='perperStream'):

    @classmethod
    def check_input_type_annotation(cls, pytype: type) -> bool:
        return True

    @classmethod
    def decode(cls, data: meta.Datum, *, trigger_metadata) -> typing.Any:
        stream_name = data.value
        return PerperCache(stream_name=stream_name)


T = typing.TypeVar('T')


class StreamHandle:
    pass


class Stream(typing.Generic[T]):
    def subscribe(self, filter_expr: str = None) -> StreamHandle:
        pass

    def rewind(self, query_expr: str = None) -> StreamHandle:
        pass


class Context:
    def fetch_state(self, state_holder: object) -> None:
        pass

    def update_state(self, state_holder: object, partial_name: str = None) -> None:
        pass

    async def start_module_async(self, name: str, payload: object) -> object:
        pass

    async def call_module_async(self, uri: str, payload: object) -> object:
        pass

    def declare_stream(self, name: str) -> Stream[T]:
        pass

    def initialize_stream(self, stream: Stream[T], *args) -> None:
        pass

    def stream_function(self, name: str, *args) -> Stream[T]:
        pass

    def stream_action(self, name: str, *args) -> None:
        pass

