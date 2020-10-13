from typing import List, Optional, Union

from httpx import Response

from neuroio.api.base import APIBase, APIBaseAsync
from neuroio.constants import SourceLicense, sentinel
from neuroio.utils import request_dict_processing, request_query_processing


class Sources(APIBase):
    def create(
        self,
        name: str,
        license_type: SourceLicense = SourceLicense.BASIC,
        identify_facesize_threshold: int = 7000,
        use_pps_time: bool = False,
        manual_create_facesize_threshold: int = 25000,
        manual_create_on_ha: bool = False,
        manual_create_on_junk: bool = False,
        manual_identify_asm: bool = True,
        auto_create_persons: bool = False,
        auto_create_facesize_threshold: int = 25000,
        auto_create_check_blur: bool = True,
        auto_create_check_exposure: bool = True,
        auto_create_on_ha: bool = False,
        auto_create_on_junk: bool = False,
        auto_check_face_angle: bool = True,
        auto_check_liveness: bool = False,
        auto_create_liveness_only: bool = True,
        auto_identify_asm: bool = True,
        store_images_for_results: Union[
            Optional[List[str]], object
        ] = sentinel,
    ) -> Response:
        data = request_dict_processing(locals(), ["self"])
        try:
            return self.client.post(url="/v1/sources/", json=data)
        finally:
            self.client.close()

    def list(
        self,
        q: str = None,
        spaces_ids: Union[List[int], object] = sentinel,
        limit: int = 20,
        offset: int = 0,
    ) -> Response:
        data = request_query_processing(locals(), ["self"])

        try:
            return self.client.get(url="/v1/sources/", params=data)
        finally:
            self.client.close()

    def get(self, id: int) -> Response:
        try:
            return self.client.get(url=f"/v1/sources/{id}/")
        finally:
            self.client.close()

    def update(
        self,
        id: int,
        name: str,
        license_type: Union[SourceLicense, object] = sentinel,
        identify_facesize_threshold: Union[int, object] = sentinel,
        use_pps_time: Union[bool, object] = sentinel,
        manual_create_facesize_threshold: Union[int, object] = sentinel,
        manual_create_on_ha: Union[bool, object] = sentinel,
        manual_create_on_junk: Union[bool, object] = sentinel,
        manual_identify_asm: Union[bool, object] = sentinel,
        auto_create_persons: Union[bool, object] = sentinel,
        auto_create_facesize_threshold: Union[int, object] = sentinel,
        auto_create_check_blur: Union[bool, object] = sentinel,
        auto_create_check_exposure: Union[bool, object] = sentinel,
        auto_create_on_ha: Union[bool, object] = sentinel,
        auto_create_on_junk: Union[bool, object] = sentinel,
        auto_check_face_angle: Union[bool, object] = sentinel,
        auto_check_liveness: Union[bool, object] = sentinel,
        auto_create_liveness_only: Union[bool, object] = sentinel,
        auto_identify_asm: Union[bool, object] = sentinel,
        store_images_for_results: Union[List[str], object] = sentinel,
    ) -> Response:
        data = request_dict_processing(locals(), ["id", "self"])

        try:
            return self.client.patch(url=f"/v1/sources/{id}/", json=data)
        finally:
            self.client.close()

    def delete(self, id: int) -> Response:
        try:
            return self.client.delete(url=f"/v1/sources/{id}/")
        finally:
            self.client.close()


class SourcesAsync(APIBaseAsync):
    async def create(
        self,
        name: str,
        license_type: SourceLicense = SourceLicense.BASIC,
        identify_facesize_threshold: int = 7000,
        use_pps_time: bool = False,
        manual_create_facesize_threshold: int = 25000,
        manual_create_on_ha: bool = False,
        manual_create_on_junk: bool = False,
        manual_identify_asm: bool = True,
        auto_create_persons: bool = False,
        auto_create_facesize_threshold: int = 25000,
        auto_create_check_blur: bool = True,
        auto_create_check_exposure: bool = True,
        auto_create_on_ha: bool = False,
        auto_create_on_junk: bool = False,
        auto_check_face_angle: bool = True,
        auto_check_liveness: bool = False,
        auto_create_liveness_only: bool = True,
        auto_identify_asm: bool = True,
        store_images_for_results: Union[
            Optional[List[str]], object
        ] = sentinel,
    ) -> Response:
        data = request_dict_processing(locals(), ["self"])
        try:
            return await self.client.post(url="/v1/sources/", json=data)
        finally:
            await self.client.aclose()

    async def list(
        self,
        q: str = None,
        spaces_ids: Union[List[int], object] = sentinel,
        limit: int = 20,
        offset: int = 0,
    ) -> Response:
        data = request_query_processing(locals(), ["self"])

        try:
            return await self.client.get(url="/v1/sources/", params=data)
        finally:
            await self.client.aclose()

    async def get(self, id: int) -> Response:
        try:
            return await self.client.get(url=f"/v1/sources/{id}/")
        finally:
            await self.client.aclose()

    async def update(
        self,
        id: int,
        name: str,
        license_type: Union[SourceLicense, object] = sentinel,
        identify_facesize_threshold: Union[int, object] = sentinel,
        use_pps_time: Union[bool, object] = sentinel,
        manual_create_facesize_threshold: Union[int, object] = sentinel,
        manual_create_on_ha: Union[bool, object] = sentinel,
        manual_create_on_junk: Union[bool, object] = sentinel,
        manual_identify_asm: Union[bool, object] = sentinel,
        auto_create_persons: Union[bool, object] = sentinel,
        auto_create_facesize_threshold: Union[int, object] = sentinel,
        auto_create_check_blur: Union[bool, object] = sentinel,
        auto_create_check_exposure: Union[bool, object] = sentinel,
        auto_create_on_ha: Union[bool, object] = sentinel,
        auto_create_on_junk: Union[bool, object] = sentinel,
        auto_check_face_angle: Union[bool, object] = sentinel,
        auto_check_liveness: Union[bool, object] = sentinel,
        auto_create_liveness_only: Union[bool, object] = sentinel,
        auto_identify_asm: Union[bool, object] = sentinel,
        store_images_for_results: Union[List[str], object] = sentinel,
    ) -> Response:
        data = request_dict_processing(locals(), ["id", "self"])

        try:
            return await self.client.patch(url=f"/v1/sources/{id}/", json=data)
        finally:
            await self.client.aclose()

    async def delete(self, id: int) -> Response:
        try:
            return await self.client.delete(url=f"/v1/sources/{id}/")
        finally:
            await self.client.aclose()
