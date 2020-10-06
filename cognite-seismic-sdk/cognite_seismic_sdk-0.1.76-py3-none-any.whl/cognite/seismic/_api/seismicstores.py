import os
from typing import *

from cognite.seismic._api.api import API
from cognite.seismic._api.utility import MaybeString, Metadata, get_identifier, get_search_spec

if not os.getenv("READ_THE_DOCS"):
    from cognite.seismic.protos.v1.seismic_service_messages_pb2 import (
        SearchSeismicStoresRequest,
        EditSeismicStoreRequest,
    )
    from cognite.seismic.protos.v1.seismic_service_datatypes_pb2 import SeismicStore, OptionalMap
else:
    from cognite.seismic._api.shims import SeismicStore


class SeismicStoreAPI(API):
    def __init__(self, query, ingestion, metadata):
        super().__init__(query=query, ingestion=ingestion, metadata=metadata)

    def search(
        self,
        *,
        id: Union[int, None] = None,
        external_id: MaybeString = None,
        external_id_substring: MaybeString = None,
        name: MaybeString = None,
        name_substring: MaybeString = None,
        get_all: bool = False,
        include_file_info: bool = False,
    ) -> Iterable[SeismicStore]:
        """Search for seismic stores.

        Can search by id, name, or substring or name. 
        Only one search method should be specified. The behaviour when multiple are specified is undefined.

        Args:
            id (int|None): Seismic store id
            external_id (str|None): Seismic store external id. NOT IMPLEMENTED
            external_id_substring (str|None): Substring of external id to search by. NOT IMPLEMENTED
            name (str|None): Seismic store name
            name_substring (str|None): Substring of name to search by
            get_all (bool): Whether to instead retrieve all visible seismic stores. Equivalent to list().
            include_file_info (bool): If true, the response will include information on the source file.
        
        Returns:
            Iterable[SeismicStore]: The list of matching seismic stores
        """
        if get_all:
            req = SearchSeismicStoresRequest(include_file_info=include_file_info)
        else:
            spec = get_search_spec(id, external_id, external_id_substring, name, name_substring)
            req = SearchSeismicStoresRequest(seismic_stores=spec, include_file_info=include_file_info)
        return self.query.SearchSeismicStores(req, metadata=self.metadata)

    def list(self, *, include_file_info: bool = False) -> Iterable[SeismicStore]:
        """List all visible seismic stores.

        List all visible seismic stores. This is equivalent to calling search() with get_all=true.
        
        Args:
            include_file_info (bool): (Optional) If true, the response will include information on the source file.

        Returns:
            Iterable[SeismicStore]: The list of visible seismic stores
        """
        return self.search(get_all=True, include_file_info=include_file_info)

    def edit(
        self,
        *,
        id: Union[int, None] = None,
        external_id: MaybeString,
        new_name: MaybeString,
        metadata: Union[Metadata, None],
    ) -> SeismicStore:
        """Edit a seismic store.

        Edit a seismic store, providing the seismic store id.
        The name and the metadata can be edited.

        Args:
            id (int | None): The id of the seismic store
            new_name (str | None): (Optional) If specified, the new name. Provide an empty string to delete the existing name.
            metadata (Dict[str, str] | None): (Optional) If specified, replaces the old metadata with the new one.
        """
        identifier = get_identifier(id, external_id)
        request = EditSeismicStoreRequest(seismic=identifier)
        if new_name is not None:
            request.name = new_name
        if metadata is not None:
            request.metadata = metadata
        return self.query.EditSeismicStore(request, metadata=self.metadata)
