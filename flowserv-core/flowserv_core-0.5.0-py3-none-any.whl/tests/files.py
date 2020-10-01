# This file is part of the Reproducible and Reusable Data Analysis Workflow
# Server (flowServ).
#
# Copyright (C) 2019-2020 NYU.
#
# flowServ is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""helper classes and methods for unit tests that perform I/O operations."""

import botocore.exceptions
import json
import os

from io import BytesIO
from typing import Dict, IO, List, Optional, Union

from flowserv.model.files.base import IOFile

import flowserv.config.api as config
import flowserv.util as util


# -- S3 Buckets ---------------------------------------------------------------

class DiskBucket(object):
    """Implementation of relevant methods for S3 buckets that are used by the
    BucketStore for test purposes. Persists all objects on disk. Uses the
    API_BASDIR if not storage directory is given.
    """
    def __init__(self, basedir: str = None):
        """Initialize the internal object dictionary."""
        self.basedir = basedir if basedir is not None else config.API_BASEDIR()

    def __repr__(self):
        """Get object representation ."""
        return "<DiskBucket dir='{}' />".format(self.basedir)

    @property
    def objects(self):
        """Simulate .objects call by returning a reference to self."""
        return self

    def delete_objects(self, Delete: Dict):
        """Delete objects in a dictionary with single key 'Objects' that points
        to a list of dictionaries with single element 'Key' referencing the
        object that is being deleted.
        """
        for obj in Delete.get('Objects'):
            filename = os.path.join(self.basedir, obj.get('Key'))
            if os.path.isfile(filename):
                os.remove(filename)

    def download_fileobj(self, key: str, data: IO):
        """Copy the buffer for the identified object into the given data
        buffer.
        """
        filename = os.path.join(self.basedir, key)
        if os.path.isfile(filename):
            with open(filename, 'rb') as f:
                data.write(f.read())
        else:
            raise botocore.exceptions.ClientError(
                operation_name='download_fileobj',
                error_response={'Error': {'Code': 404, 'Message': filename}}
            )
        data.seek(0)

    def filter(self, Prefix: str) -> List:
        """Return all objects in the bucket that have a key which matches the
        given prefix.
        """
        result = list()
        for key in parse_dir(self.basedir, ''):
            if key.startswith(Prefix):
                result.append(ObjectSummary(key))
        return result

    def upload_fileobj(self, file: IO, dst: str):
        """Add given buffer to the object index. Uses the destination as the
        object key.
        """
        filename = os.path.join(self.basedir, dst)
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'wb') as f:
            f.write(file.read())


def DiskStore(basedir):
    """Create an instance of the buckect store with a disk bucket."""
    from flowserv.model.files.s3 import BucketStore
    return BucketStore(DiskBucket(basedir))


class ObjectSummary(object):
    """Simple class to simulate object summaries. Only implements the .key
    property.
    """
    def __init__(self, key):
        """Initialize the object key."""
        self.key = key


def parse_dir(dirname, prefix, result=None):
    result = result if result is not None else list()
    for filename in os.listdir(dirname):
        f = os.path.join(dirname, filename)
        if os.path.isdir(f):
            parse_dir(
                dirname=f,
                prefix=os.path.join(prefix, filename),
                result=result
            )
        else:
            result.append(os.path.join(prefix, filename))
    return result


# -- Helper Functions ---------------------------------------------------------


def io_file(data: Union[List, Dict], format: Optional[str] = None) -> IOFile:
    """Write simple text to given bytes buffer."""
    buf = BytesIO()
    buf.seek(0)
    if format is None or format == util.FORMAT_JSON:
        buf.write(str.encode(json.dumps(data)))
    else:
        for line in data:
            buf.write(str.encode('{}\n'.format(line)))
    return IOFile(buf)
