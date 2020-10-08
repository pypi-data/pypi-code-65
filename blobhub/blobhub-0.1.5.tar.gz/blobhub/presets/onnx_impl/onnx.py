import logging
import os.path
import tarfile
from typing import List
from pathlib import Path

from blobhub.blob import Blob, Revision
from .config import Config
from .model import Model
from .uploader import Uploader
from .downloader import Downloader


logger = logging.getLogger("blobhub")


class ModelUploadFailure(Exception):

    def __init__(self, model: Model, message: str) -> None:
        super().__init__(message)
        self.model = model

class ModelDownloadFailure(Exception):

    def __init__(self, message: str) -> None:
        super().__init__(message)


class Onnx:

    def __init__(self, revision: Revision, config=Config()):
        self.config = config
        self.revision = revision

    def upload(self, model: Model) -> bool:
        try:
            # Package the model
            logger.info("Packaging the model...")
            model_path_and_file_name, _ = os.path.splitext(model.path)
            archived_path = "{}.tar.gz".format(model_path_and_file_name)
            with tarfile.open(archived_path, "w:gz") as tar:
                tar.add(model.path, arcname="model.onnx")
            logger.info("Model archive is ready to be uploaded")

            # Pick upload type based on config preference or file size
            file_size = self._get_file_size(archived_path)
            if ( self.config.force_multipart_upload or
                    file_size > self.config.upload_maximum_payload_size ):
                return self._upload_multiple_parts(path=archived_path, size=file_size)
            else:
                return self._upload_single_part(path=archived_path)
        except Exception as e:
            raise ModelUploadFailure(model=model, message=str(e))

    def download(self) -> Model:
        try:
            # Describe the model
            model_components = self._describe_model()
            model_archive = self._find_model_component(components=model_components, path="model.tar.gz")
            archive_size = model_archive["size"]

            # Prepare paths
            prefix_path = os.path.join(
                self.config.data_folder_path,
                self.revision.blob[Blob.FIELD_ID],
                self.revision[Revision.FIELD_ID])
            model_path = os.path.join(
                prefix_path,
                "model.onnx")
            archived_path = os.path.join(
                prefix_path,
                "model.tar.gz")

            # Create folders to the location where model is stored
            os.makedirs(prefix_path, exist_ok=True)

            # Pick download method based on file size
            if ( self.config.force_multipart_download or
                    archive_size > self.config.download_maximum_payload_size ):
                success = self._download_multiple_parts(archived_path)
            else:
                success = self._download_single_part(archived_path)
            if not success:
                raise Exception("failed_to_download")

            # Unpack the model
            logger.info("Unpacking the model...")
            with tarfile.open(archived_path, "r:gz") as tar:
                tar.extractall(path=prefix_path)
            logger.info("Model is unpacked and is ready to be used")
        except Exception as e:
            raise ModelDownloadFailure(message=str(e))

        # Construct model object
        return Model(onnx=self, path=model_path)

    """
    Upload - Single Part 
    """

    def _upload_single_part(self, path: str) -> bool:
        """
        :param path: Path to the artifact to be uploaded.
        :return: Boolean value indicating whether operation succeeded or not.
        """

        # Load model data
        with open(path, "rb") as model_file:
            model_data = model_file.read()

        # Upload model data
        request_body = {
            "engine": "onnx",
            "command": "upload",
            "path": "model.tar.gz",
            "size": self._get_file_size(path)
        }
        response_body, _ = self.revision.blob.api.revisions_revision_id_data_command_post(
            revision_id=self.revision.revision_id,
            body=request_body,
            data=model_data
        )

        # Confirm successful upload
        success = "success" == response_body["status"]
        return success

    """
    Upload - Multiple Parts 
    """

    def _upload_multiple_parts(self, path: str, size: int) -> bool:
        """
        :param path: Path to the artifact to be uploaded.
        :return: Boolean value indicating whether operation succeeded or not.
        """

        uploader = Uploader(self, path, size)
        success = uploader.upload()
        return success

    """
    Download - Single Part 
    """

    def _describe_model(self):
        request_body = {
            "engine": "onnx",
            "command": "describe"
        }
        response_body, _ = self.revision.blob.api.revisions_revision_id_data_query_post(
            revision_id=self.revision.revision_id,
            body=request_body
        )
        return response_body["components"]

    @staticmethod
    def _find_model_component(components: List[dict], path: str):
        for component in components:
            if component["path"] == path:
                return component
        raise Exception("component_not_found")

    def _download_single_part(self, path):
        """
        :param path: Path to the location of model archive.
        :return: Boolean value indicating whether operation succeeded or not.
        """

        # Download model data
        request_body = {
            "engine": "onnx",
            "command": "download",
            "path": "model.tar.gz"
        }
        request_headers = {
            "Accept": "application/octet-stream"
        }
        response_body, response_data = self.revision.blob.api.revisions_revision_id_data_query_post(
            revision_id=self.revision.revision_id,
            body=request_body,
            headers=request_headers
        )

        # Save model data
        with open(path, "wb") as model_file:
            model_file.write(response_data)

        # Confirm successful download
        success = "success" == response_body["status"]
        return success

    """
    Download - Multiple Parts 
    """

    def _download_multiple_parts(self, path):
        """
        :param path: Path to the location of model archive.
        :return: Boolean value indicating whether operation succeeded or not.
        """

        downloader = Downloader(self, path)
        success = downloader.download()
        return success

    """
    File Operations
    """

    @staticmethod
    def _get_file_size(path):
        return Path(path).stat().st_size
