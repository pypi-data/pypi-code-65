"""
Uploader that uploads files into Cloud storage
"""

import os
import boto3


class S3DatastoreUploader:
    """
    This class uploads directory into S3

    Attributes
    ----------
    user_id: str
        Id of user
    source_file: str
        Source file to upload
    datastore: str
        Name of the datastore
    version: str
        Version of the datastore
    size: int
        Original files size in bytes
    """
    def __init__(self, user_id: str, source_file: str, datastore: str,
                 version: str, size: int):
        self.user_id = user_id
        self.source_file = source_file
        self.datastore = datastore
        self.version = version
        self.size = size

    @property
    def target_bucket(self):
        return f"gridai-{self.user_id}"

    @property
    def target_data_path(self):
        """
        Get target S3 data path
        """
        return f"datastores/{self.datastore}/versions/" \
               f"{self.version}/data/"

    def upload(self):
        """
        Upload files from source dir into target path in S3
        """
        s3 = boto3.client('s3')
        s3.create_bucket(Bucket=self.target_bucket)

        # Write the orginal content size
        size_obj = boto3.resource('s3').Object(
            self.target_bucket, os.path.join(self.target_data_path, "size"))
        size_obj.put(Body=str(self.size))

        s3 = boto3.client('s3')
        s3.create_bucket(Bucket=self.target_bucket)
        s3.upload_file(self.source_file, self.target_bucket,
                       os.path.join(self.target_data_path, "data.tar.gz"))
