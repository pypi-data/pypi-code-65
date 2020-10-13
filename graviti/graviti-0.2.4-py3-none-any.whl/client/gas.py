#!/usr/bin/env python3
#
# Copyright 2020 Graviti. All Rights Reserved.
#

"""This file defines class GAS."""

from typing import Any, Dict, List, Optional, Tuple, Type, Union, overload
from urllib.parse import urljoin

from typing_extensions import Literal

from ..dataset import Dataset, FusionDataset
from ..label import LabelTables
from .dataset import DatasetClient, FusionDatasetClient
from .exceptions import GASDatasetError, GASDatasetTypeError, GASLabelsetError, GASLabelsetTypeError
from .labelset import FusionLabelsetClient, LabelsetClient, LabelsetClientBase
from .requests import Client, get

DatasetClientType = Union[DatasetClient, FusionDatasetClient]
LabelsetClientType = Union[LabelsetClient, FusionLabelsetClient]


class GAS:
    """This is a class defining the concept of TensorBay.
    It mainly defines some operations on datasets.

    :param access_key: user's access key
    :param url: the url of the gas website
    """

    _VERSIONS = {1: "COMMUNITY", 2: "ENTERPRISE"}

    def __init__(self, access_key: str, url: str = "") -> None:
        self._client = Client(access_key, url)

    def get_user_info(self) -> Dict[str, str]:
        """Get the user info corresponding to the AccessKey

        :return: A directory which contains the username and clientTag
        """
        post_data = {"token": self._client.access_key}
        url = urljoin(self._client.gateway_url, "user/api/v3/token/get-user-profile")
        response = get(url, post_data)
        return {
            "username": response["userName"],
            "version": GAS._VERSIONS[response["clientTag"]],
        }

    @overload
    def _create_dataset(
        self,
        name: str,
        is_continuous: bool,
        is_fusion: Literal[False],
    ) -> DatasetClient:
        ...

    @overload
    def _create_dataset(
        self,
        name: str,
        is_continuous: bool,
        is_fusion: Literal[True],
    ) -> FusionDatasetClient:
        ...

    def _create_dataset(
        self,
        name: str,
        is_continuous: bool,
        is_fusion: bool,
    ) -> DatasetClientType:
        post_data = {
            "name": name,
            "contentSetType": int(is_fusion),  # normal dataset: 0, fusion dataset: 1
            "isContinuous": int(is_continuous),
        }
        data = self._client.dataset_post("createContentSet", post_data)
        dataset_id = data["contentSetId"]
        ReturnType: Type[DatasetClientType] = FusionDatasetClient if is_fusion else DatasetClient
        return ReturnType(name, dataset_id, self._client)

    def create_dataset(self, name: str, is_continuous: bool = False) -> DatasetClient:
        """Create a dataset with the input name,
        and return the client of the created dataset

        :param name: Name of the dataset, unique for a user
        :param is_continuous: Whether the data in dataset are continuous,
            `True` for continuous data, `False` for Discontinuous data
        :return: The client of the created dataset
        """
        return self._create_dataset(name, is_continuous, False)

    def create_fusion_dataset(self, name: str, is_continuous: bool = False) -> FusionDatasetClient:
        """Create a fusion dataset with the input name,
        and return the client of the created fusion dataset

        :param name: Name of the fusion dataset, unique for a user
        :param is_continuous: Whether the data in dataset are continuous,
            `True` for continuous data, `False` for Discontinuous data
        :return: The client of the created fusion dataset
        """
        return self._create_dataset(name, is_continuous, True)

    def _get_dataset_id_and_type(self, name: str) -> Tuple[str, bool]:
        """Get the dataset ID of the dataset with the input name no matter the type of the dataset

        :param name: The name of the requested dataset
        :raises GASDatasetError: When the requested dataset does not exist
        :return: The tuple of dataset ID and type (`True` for fusion dataset)
        """
        if not name:
            raise GASDatasetError(name)

        datasets_info = self._list_datasets_info(name)
        if not datasets_info:
            raise GASDatasetError(name)

        response = datasets_info[0]["contentSetResp"]
        is_fusion = bool(response["contentSetType"])
        return (response["contentSetId"], is_fusion)

    def _get_dataset(self, name: str) -> DatasetClientType:
        """Get the client of the dataset with the input name no matter the type of the dataset

        :param name: The name of the requested dataset
        :raises GASDatasetError: When the requested dataset does not exist
        :return: The client of the request dataset
        """
        dataset_id, is_fusion = self._get_dataset_id_and_type(name)
        ReturnType: Type[DatasetClientType] = FusionDatasetClient if is_fusion else DatasetClient
        return ReturnType(name, dataset_id, self._client)

    def get_dataset(self, name: str) -> DatasetClient:
        """Get the client of the dataset with the input name

        :param name: The name of the requested dataset
        :raises GASDatasetError: When the requested dataset does not exist
        :raises GASDatasetTypeError: When requested dataset is a fusion dataset
        :return: The client of the request dataset
        """
        client = self._get_dataset(name)
        if not isinstance(client, DatasetClient):
            raise GASDatasetTypeError(name, True)

        return client

    def get_fusion_dataset(self, name: str) -> FusionDatasetClient:
        """Get the client of the fusion dataset with the input name

        :param name: The name of the requested fusion dataset
        :raises GASDatasetError: When the requested dataset does not exist
        :raises GASDatasetTypeError: When requested dataset is not a fusion dataset
        :return: The client of the request fusion dataset
        """
        client = self._get_dataset(name)
        if not isinstance(client, FusionDatasetClient):
            raise GASDatasetTypeError(name, False)

        return client

    def get_or_create_dataset(self, name: str, is_continuous: bool = False) -> DatasetClient:
        """Get a dataset if 'name' exists. Create one otherwise.

        :param name: The name of a dataset
        :param is_continuous: Whether the data in dataset are continuous,
            `True` for continuous data, `False` for Discontinuous data
        :raises GASDatasetTypeError: When requested dataset is a fusion dataset
        :return: created dataset
        """
        try:
            return self.get_dataset(name)
        except GASDatasetError:
            return self.create_dataset(name, is_continuous)

    def get_or_create_fusion_dataset(
        self,
        name: str,
        is_continuous: bool = False,
    ) -> FusionDatasetClient:
        """Get a dataset if 'name' exists. Create one otherwise.

        :param name: The name of a dataset
        :param is_continuous: Whether the data in dataset are continuous,
            `True` for continuous data, `False` for Discontinuous data
        :raises GASDatasetTypeError: When requested dataset is not a fusion dataset
        :return: created dataset
        """
        try:
            return self.get_fusion_dataset(name)
        except GASDatasetError:
            return self.create_fusion_dataset(name, is_continuous)

    def _create_labelset(
        self,
        dataset_id: str,
        label_tables: LabelTables,
        remote_paths: Optional[List[str]] = None,
    ) -> str:
        """Create a labelset and return the labelset ID.

        :param label_tables: A LabelTables covers all labels of the labelset
        :param remote_paths: A list of remote paths
        :return: The labelset ID of created labelset
        """
        post_data = {
            "contentSetId": dataset_id,
            "type": LabelsetClientBase.TYPE_GROUND_TRUTH,
            "version": "v1.0.2",
        }
        metadata = LabelsetClientBase.create_metadata(label_tables)
        if metadata:
            post_data["meta"] = metadata
        if remote_paths:
            post_data["objectPaths"] = remote_paths

        data = self._client.labelset_post("createLabelSet", post_data)
        labelset_id = data["labelSetId"]
        return labelset_id  # type: ignore[no-any-return]

    def create_labelset(
        self,
        dataset_name: str,
        label_tables: LabelTables,
        remote_paths: Optional[List[str]] = None,
    ) -> LabelsetClient:
        """Create a labelset.

        :param label_tables: A LabelTables covers all labels of the labelset
        :param remote_paths: A list of remote paths
        :return: The client of the created labelset
        """
        dataset_id, is_fusion = self._get_dataset_id_and_type(dataset_name)
        if is_fusion:
            raise GASDatasetTypeError(dataset_name, True)

        labelset_id = self._create_labelset(dataset_id, label_tables, remote_paths)
        return LabelsetClient(labelset_id, dataset_name, self._client)

    def create_fusion_labelset(
        self,
        dataset_name: str,
        label_tables: LabelTables,
        remote_paths: Optional[List[str]] = None,
    ) -> FusionLabelsetClient:
        """Create a labelset.

        :param label_tables: A LabelTables covers all labels of the labelset
        :param remote_paths: A list of remote paths
        :return: The client of the created fusion labelset
        """
        dataset_id, is_fusion = self._get_dataset_id_and_type(dataset_name)
        if not is_fusion:
            raise GASDatasetTypeError(dataset_name, False)

        labelset_id = self._create_labelset(dataset_id, label_tables, remote_paths)
        return FusionLabelsetClient(labelset_id, dataset_name, self._client)

    def _get_labelset_type_and_dataset_name(self, labelset_id: str) -> Tuple[bool, str]:
        if not labelset_id:
            raise GASLabelsetError(labelset_id)

        post_data = {
            "id": labelset_id,
            "projection": {"contentSetType": 1, "contentSetName": 1},
        }

        summaries = self._client.labelset_post("listLabelSetSummaries", post_data)[
            "labelSetSummaries"
        ]
        if not summaries:
            raise GASLabelsetError(labelset_id)

        return (bool(summaries[0]["contentSetType"]), summaries[0]["contentSetName"])

    def get_labelset(self, labelset_id: str) -> LabelsetClient:
        """Get the client of the labelset with the input labelset_id

        :param labelset_id: The labelset ID of the requested labelset
        :raises GASLabelsetError: When the requested labelset does not exist
        :return: The client of the requested labelset
        """
        is_fusion, dataset_name = self._get_labelset_type_and_dataset_name(labelset_id)
        if is_fusion:
            raise GASLabelsetTypeError(labelset_id, True)

        return LabelsetClient(labelset_id, dataset_name, self._client)

    def get_fusion_labelset(self, labelset_id: str) -> FusionLabelsetClient:
        """Get the client of the fusion labelset with the input labelset_id

        :param labelset_id: The labelset ID of the requested fusion labelset
        :raises GASLabelsetError: When the requested fusion labelset does not exist
        :return: The client of the requested fusion labelset
        """
        is_fusion, dataset_name = self._get_labelset_type_and_dataset_name(labelset_id)
        if not is_fusion:
            raise GASLabelsetTypeError(labelset_id, False)

        return FusionLabelsetClient(labelset_id, dataset_name, self._client)

    def list_labelsets(self, dataset_name: str) -> List[str]:
        """List ids of all labelsets of the dataset.

        :param dataset_name: list the labelset with input dataset name. If `None`, list all
        :return: A list of labelsets ids
        """
        dataset_id, _ = self._get_dataset_id_and_type(dataset_name)
        post_data = {
            "contentSetId": dataset_id,
            "projection": {"id": 1},
            "ignoreContentSetInfo": True,
            "pageSize": -1,
        }

        summaries = self._client.labelset_post("listLabelSetSummaries", post_data)[
            "labelSetSummaries"
        ]
        return [summary["id"] for summary in summaries]

    def delete_labelset(self, labelset_id: str) -> None:
        """Delete a labelset according to a labelset id.

        :param labelset_id: The id of the labelset to be deleted
        """
        post_data = {"labelSetId": labelset_id}
        self._client.labelset_post("deleteLabelSet", post_data)

    @overload
    def upload_dataset_object(
        self,
        dataset: Dataset,
        *,
        jobs: int = 1,
        skip_uploaded_files: bool = False,
    ) -> DatasetClient:
        ...

    @overload
    def upload_dataset_object(
        self,
        dataset: FusionDataset,
        *,
        jobs: int = 1,
        skip_uploaded_files: bool = False,
    ) -> FusionDatasetClient:
        ...

    @overload
    def upload_dataset_object(
        self,
        dataset: Union[Dataset, FusionDataset],
        *,
        jobs: int = 1,
        skip_uploaded_files: bool = False,
    ) -> DatasetClientType:
        ...

    def upload_dataset_object(
        self,
        dataset: Union[Dataset, FusionDataset],
        *,
        jobs: int = 1,
        skip_uploaded_files: bool = False,
    ) -> DatasetClientType:
        """Upload a `Dataset` or `FusionDataset` to TensorBay,
        This function will upload all info contains in the `Dataset` or `FusionDataset` object,
        which includes:
        - Create a dataset using the name and type of input `Dataset` or `FusionDataset`,
        - Upload all `Segment` or `FusionSegment` in the dataset to TensorBay

        :param dataset: The `Dataset` or `FusionDataset` object needs to be uploaded.
        :param jobs: The number of the max workers in multithread upload
        :param skip_uploaded_files: Set it to `True` to skip the uploaded files
        :return: The `DatasetClient` or `FusionDatasetClient` used for uploading the dataset
        """
        dataset_client: DatasetClientType

        if isinstance(dataset, FusionDataset):
            dataset_client = self.get_or_create_fusion_dataset(dataset.name, dataset.is_continuous)
        else:
            dataset_client = self.get_or_create_dataset(dataset.name, dataset.is_continuous)

        for segment in dataset:
            dataset_client.upload_segment_object(
                segment,  # type: ignore[arg-type]
                jobs=jobs,
                skip_uploaded_files=skip_uploaded_files,
            )

        return dataset_client

    def list_datasets(self) -> List[str]:
        """List names of all datasets.

        :return: A list of names of all datasets
        """
        datasets_info = self._list_datasets_info()
        dataset_names: List[str] = []
        for dataset_info in datasets_info:
            dataset_name = dataset_info["contentSetResp"]["name"]
            dataset_names.append(dataset_name)
        return dataset_names

    def delete_dataset(self, name: str) -> None:
        """Delete a dataset according to its name.

        :param name: The name of the dataset to delete
        :raises GASDatasetError: When the requested dataset does not exist
        """
        dataset_id, _ = self._get_dataset_id_and_type(name)
        post_data = {"contentSetId": dataset_id, "name": name}
        self._client.dataset_post("deleteContentSets", post_data)

    def _list_datasets_info(self, name: Optional[str] = None) -> List[Any]:
        """List info of all datasets.

        :param name: dataset name to list its info. If None, list info of all datasets
        :return: A list of dicts containing dataset info. If name does not exist,
            return an empty list.
        """
        post_data = {"name": name, "pageSize": -1}
        data = self._client.dataset_post("listContentSets", post_data)
        return data["contentSets"]  # type: ignore[no-any-return]

    @overload
    def upload_labelset_object(
        self,
        dataset: Dataset,
        labelset_id: Optional[str] = None,
        *,
        jobs: int = 1,
        skip_uploaded_files: bool = False,
    ) -> LabelsetClient:
        ...

    @overload
    def upload_labelset_object(
        self,
        dataset: FusionDataset,
        labelset_id: Optional[str] = None,
        *,
        jobs: int = 1,
        skip_uploaded_files: bool = False,
    ) -> FusionLabelsetClient:
        ...

    @overload
    def upload_labelset_object(
        self,
        dataset: Union[Dataset, FusionDataset],
        labelset_id: Optional[str] = None,
        *,
        jobs: int = 1,
        skip_uploaded_files: bool = False,
    ) -> LabelsetClientType:
        ...

    def upload_labelset_object(
        self,
        dataset: Union[Dataset, FusionDataset],
        labelset_id: Optional[str] = None,
        *,
        jobs: int = 1,
        skip_uploaded_files: bool = False,
    ) -> LabelsetClientType:
        """Upload the label in `Dataset` or `FusionDataset` to TensorBay,
        This function will upload all label info contains in the `Dataset` or `FusionDataset`,
        which includes:
        - Create a labelset using the name and type of input `Dataset` or `FusionDataset`,
        - Upload all `Segment` or `FusionSegment` in the dataset to TensorBay

        :param dataset: The `Dataset` or `FusionDataset` object needs to be uploaded.
        :param lableset_id: The target labelset_id, if empty, new labelset will be created
        :param jobs: The number of the max workers in multithread upload
        :param skip_uploaded_files: Set it to `True` to skip the uploaded files
        :return: The `LabelsetClient` or `FusionLabelsetClient` used for uploading the label
        """
        labelset_client: LabelsetClientType

        if isinstance(dataset, FusionDataset):
            if labelset_id:
                labelset_client = self.get_fusion_labelset(labelset_id)
            else:
                labelset_client = self.create_fusion_labelset(dataset.name, dataset.label_tables)
        else:
            if labelset_id:
                labelset_client = self.get_labelset(labelset_id)
            else:
                labelset_client = self.create_labelset(dataset.name, dataset.label_tables)

        for segment in dataset:
            labelset_client.upload_segment_object(
                segment,  # type: ignore[arg-type]
                jobs=jobs,
                skip_uploaded_files=skip_uploaded_files,
            )

        return labelset_client
