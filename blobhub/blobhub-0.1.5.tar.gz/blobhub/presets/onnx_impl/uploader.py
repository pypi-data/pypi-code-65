import logging

import requests

from blobhub.api import Decorators, CallFailure, Api


logger = logging.getLogger("blobhub")


class Uploader:
    """
    Implements multi-part model upload functionality
    """

    def __init__(self, onnx: "Onnx", path: str, size: int) -> None:
        self.onnx = onnx
        self.path = path
        self.size = size
        self.model_file = None
        self.upload_operation_id = None
        self.upload_operation = None
        self.uploaded_parts = None

    def upload(self) -> bool:
        try:
            self._open_file()
            self._initiate_model_upload()
            self._upload_parts()
            success = self._complete_upload()
            return success
        except Exception:
            self._cancel_upload()
            return False

    """
    Internals
    """

    def _open_file(self):
        self.model_file = open(self.path, "rb")

    def _initiate_model_upload(self):
        logger.info("Initiating model upload...")

        request_body = {
            "engine": "onnx",
            "command": "initiate_upload",
            "path": "model.tar.gz",
            "size": self.size
        }
        response_body, _ = self.onnx.revision.blob.api.revisions_revision_id_data_command_post(
            revision_id=self.onnx.revision.revision_id,
            body=request_body
        )
        self.upload_operation_id = response_body["operation_id"]
        self.upload_operation = response_body["operation"]

    def _upload_parts(self):
        self.uploaded_parts = []
        for index, part in enumerate(self.upload_operation["parts"]):
            logger.info("Uploading part {} of {}...".format(index + 1, len(self.upload_operation["parts"])))

            # Read the data from local file
            self.model_file.seek(part["offset"])
            data = self.model_file.read(part["size"])

            # Upload the part
            hash = self._upload_part(
                url=part["upload"]["url"],
                headers=part["upload"]["headers"],
                data=data)

            # Remember part details
            self.uploaded_parts.append({
                "hash": hash
            })

            logger.info("Part {} is uploaded".format(index + 1))

    @Decorators.retriable
    def _upload_part(self, url: str, headers: dict, data: bytes) -> str:
        try:
            response = requests.put(
                url=url,
                headers=headers,
                data=data
            )
            if 0 == response.status_code or response.status_code >= 500:
                raise CallFailure()
            hash = response.headers["ETag"]
            return hash
        except Exception:
            raise CallFailure()

    def _complete_upload(self) -> bool:
        self.model_file.close()

        request_body = {
            "engine": "onnx",
            "command": "complete_upload",
            "operation_id": self.upload_operation_id,
            "parts": self.uploaded_parts
        }
        response_body, _ = self.onnx.revision.blob.api.revisions_revision_id_data_command_post(
            revision_id=self.onnx.revision.revision_id,
            body=request_body
        )
        success = Api.is_response_successful(response=response_body)

        logger.info("Model uploaded completed with status: {}".format(success))

        return success

    def _cancel_upload(self):
        if self.model_file is not None:
            self.model_file.close()

        if self.upload_operation_id is not None:
            request_body = {
                "engine": "onnx",
                "command": "cancel_upload",
                "operation_id": self.upload_operation_id
            }
            self.onnx.revision.blob.api.revisions_revision_id_data_command_post(
                revision_id=self.onnx.revision.revision_id,
                body=request_body
            )
