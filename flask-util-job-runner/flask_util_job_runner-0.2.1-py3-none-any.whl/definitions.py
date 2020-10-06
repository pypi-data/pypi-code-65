import os
from pathlib import Path

from minio import Minio

ROOT_DIR = Path(__file__).parent.absolute()
REDIS_ADDRESS = 'redis-master.redis'

LANGUAGE_ID_FILE_NAME = 'lid.176.bin'
LANGUAGE_ID_BUCKET_NAME = 'apps-resources'
BUCKET_NAME = 'test'

MINIO_ADDRESS = 'minio-hl.minio'


def get_minio_client():
    return Minio(MINIO_ADDRESS + ':9000',
                 access_key=os.environ.get('MINIO_ACCESS_KEY'),
                 secret_key=os.environ.get('MINIO_SECRET_KEY'),
                 secure=False)
