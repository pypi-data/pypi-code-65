import os
from typing import *

from cognite.seismic._api.api import API
from cognite.seismic._api.utility import MaybeString, Metadata, get_identifier, get_search_spec

if not os.getenv("READ_THE_DOCS"):
    from cognite.seismic.protos.v1.seismic_service_messages_pb2 import (
        CreatePartitionRequest,
        SearchPartitionsRequest,
        EditPartitionRequest,
        DeletePartitionRequest,
    )
    from cognite.seismic.protos.v1.seismic_service_datatypes_pb2 import Partition, SearchSpec, Identifier
else:
    from cognite.seismic._api.shims import Partition


class PartitionAPI(API):
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
    ) -> Iterable[Partition]:
        """Search for partitions.
        
        Can search by id, external_id, name, or substrings of external_id or name. 
        Only one search method should be specified. The behaviour when multiple are specified is undefined.

        Args:
            id (int|None): Partition id
            external_id (str|None): Partition external id
            external_id_substring (str|None): Substring of external id to search by
            name (str|None): Partition name
            name_substring (str|None): Substring of name to search by
            get_all (bool): Whether to instead retrieve all visible partitions. Equivalent to list().
        
        Returns:
            Iterable[Partition]: The list of matching partitions
        """
        spec = get_search_spec(id, external_id, external_id_substring, name, name_substring)

        if get_all:
            req = SearchPartitionsRequest()
        else:
            req = SearchPartitionsRequest(partitions=spec)
        return self.query.SearchPartitions(req, metadata=self.metadata)

    def list(self) -> Iterable[Partition]:
        """List all partitions.

        List all visible partitions. This is equivalent to calling search() with get_all=true.

        Returns:
            Iterable[Partition]: All visible partitions
        """

        return self.search(get_all=True)

    def create(self, *, external_id: str, name: str = "") -> Partition:
        """Create a new partition.

        Create a new partition, providing an external id and an optional name.

        Args:
            external_id (str): The external id of the new partition. Must be unique.
            name (str): (Optional) The name of the new partition. If not specified, will display the external id wherever a name is required.
        """
        createRequest = CreatePartitionRequest(name=name, external_id=external_id)
        return self.query.CreatePartition(createRequest, metadata=self.metadata)

    def edit(self, *, id: Union[int, None] = None, external_id: MaybeString = None, new_name: str) -> Partition:
        """Edit an existing partition.

        Edit an existing partition by providing either an id or an external id.
        The only parameter that can be edited is the name.

        Args:
            id (int | None): The id of the partition
            external_id (str | None): The external id of the partition
            new_name (str): The new name. Set as an empty string to delete the existing name.
        """
        identifier = get_identifier(id, external_id)
        editRequest = EditPartitionRequest(partition=identifier, new_name=new_name)
        return self.query.EditPartition(editRequest, metadata=self.metadata)

    def delete(self, *, id: Union[int, None] = None, external_id: MaybeString = None) -> bool:
        """Delete a partition.

        Delete a partition by providing either an id or an external id.

        Args:
            id (int | None): The id of the partition
            external_id (str | None): The external id of the partition
        """
        identifier = get_identifier(id, external_id)
        deleteRequest = DeletePartitionRequest(partition=identifier)
        return self.query.DeletePartition(deleteRequest, metadata=self.metadata).success
