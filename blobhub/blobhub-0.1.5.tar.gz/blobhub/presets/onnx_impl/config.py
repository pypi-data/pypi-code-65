from pathlib import Path


BLOBHUB_FOLDER_NAME = ".blobhub"

def default_home_path():
    return "{}/{}".format(Path.home(), BLOBHUB_FOLDER_NAME)


class Config:

    UPLOAD_MAXIMUM_PAYLOAD_SIZE = 4 * 1024 * 1024
    DOWNLOAD_MAXIMUM_PAYLOAD_SIZE = 4 * 1024 * 1024

    def __init__(
            self,
            data_folder_path=default_home_path(),
            force_multipart_upload=False,
            force_multipart_download=False):
        self.data_folder_path = data_folder_path
        self.force_multipart_upload = force_multipart_upload
        self.force_multipart_download = force_multipart_download
        self.upload_maximum_payload_size = self.UPLOAD_MAXIMUM_PAYLOAD_SIZE
        self.download_maximum_payload_size = self.DOWNLOAD_MAXIMUM_PAYLOAD_SIZE
