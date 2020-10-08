import logging

import requests

from blobhub.api import Decorators, CallFailure


logger = logging.getLogger("blobhub")


class Downloader:
    """
    Implements multi-part model download functionality
    """

    def __init__(self, onnx: "Onnx", path: str) -> None:
        self.onnx = onnx
        self.path = path
        self.model_file = None
        self.download_operation = None

    def download(self):
        try:
            self._open_file()
            self._initiate_model_download()
            self._download_parts()
            self._close_file()
            logger.info("Model download completed")
            return True
        except Exception:
            self._close_file()
            return False

    """
    Internals
    """

    def _open_file(self):
        self.model_file = open(self.path, "wb+")

    def _initiate_model_download(self):
        logger.info("Initiating model download...")

        request_body = {
            "engine": "onnx",
            "command": "initiate_download",
            "path": "model.tar.gz"
        }
        response_body, _ = self.onnx.revision.blob.api.revisions_revision_id_data_query_post(
            revision_id=self.onnx.revision.revision_id,
            body=request_body
        )
        self.download_operation = response_body["operation"]

    def _download_parts(self):
        for index, part in enumerate(self.download_operation["parts"]):
            logger.info("Downloading part {} of {}...".format(index + 1, len(self.download_operation["parts"])))

            # Download the part
            data = self._download_part(
                url=part["download"]["url"],
                headers=part["download"]["headers"])

            # Write data to local file
            self.model_file.write(data)

            logger.info("Part {} is downloaded".format(index + 1))

    @Decorators.retriable
    def _download_part(self, url: str, headers: dict) -> bytes:
        try:
            response = requests.get(
                url=url,
                headers=headers
            )
            if 0 == response.status_code or response.status_code >= 500:
                raise CallFailure()
            return response.content
        except Exception:
            raise CallFailure()

    def _close_file(self):
        if self.model_file is not None:
            self.model_file.close()
