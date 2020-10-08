import os
import logging
from google.cloud import storage
import urllib.request


def upload_url_to_gcs(source_file_url: str,
                      source_file_content_type: str,
                      destination_bucket_name: str,
                      destination_file_name: str):
    """
    Loads a file directly from a public URL to a GCS bucket

    Args:
        source_file_url (string): public URL to file
        source_file_content_type (string): MIME Type (e.g. 'text/csv' or 'application/json')
        destination_bucket_name (string): destination GCS bucket name (without gs:// prefix and without folder)
        destination_file_name (string): destination file name, including extension and with folder prefix if required
    """

    try:
        # get project from environment variable and initialise client
        project_id = os.environ.get('GCP_PROJECT')
        GCS = storage.Client(project=project_id)

        # get file and assign to variable
        file = urllib.request.urlopen(source_file_url)

        # upload file to GCS bucket
        bucket = GCS.get_bucket(destination_bucket_name)
        blob = bucket.blob(destination_file_name)
        blob.upload_from_string(file.read(), content_type=source_file_content_type)
        logging.info(f"{destination_file_name} {source_file_content_type} file loaded from {source_file_url} to gs://{destination_bucket_name}")
        status = "success"

    except Exception as e:
        logging.exception(str(e))
        status = "fail"

    return status
