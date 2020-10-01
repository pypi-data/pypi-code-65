from . import rest_api
from . import config
from . import client
from . import cloudarray
from . import tiledb_cloud_error
from .rest_api import ApiException as GenApiException
from .rest_api import rest
from . import udf
from . import utils

import zlib
import multiprocessing
import cloudpickle
import urllib
import base64
import sys


class UDFResult(multiprocessing.pool.ApplyResult):
    def __init__(self, response):
        self.response = response
        self.task_id = None

    def get(self, timeout=None):
        try:
            response = rest.RESTResponse(self.response.get(timeout=timeout))

            self.task_id = response.getheader(client.TASK_ID_HEADER)
            cloudarray.last_udf_task_id = self.task_id

            res = response.data

        except GenApiException as exc:
            raise tiledb_cloud_error.check_udf_exc(exc) from None
        except multiprocessing.TimeoutError as exc:
            raise tiledb_cloud_error.check_udf_exc(exc) from None

        if res[:2].hex() in ["7801", "785e", "789c", "78da"]:
            try:
                res = zlib.decompress(res)
            except zlib.error:
                raise tiledb_cloud_error.TileDBCloudError(
                    "Failed to decompress (zlib) result object"
                )

        try:
            res = cloudpickle.loads(res)
        except:
            raise tiledb_cloud_error.TileDBCloudError(
                "Failed to load cloudpickle result object"
            )

        return res


def info(uri):
    """
    Returns the cloud metadata

    :return: metadata object
    """
    (namespace, array_name) = split_uri(uri)
    api_instance = client.client.array_api

    try:
        return api_instance.get_array_metadata(namespace=namespace, array=array_name)
    except GenApiException as exc:
        raise tiledb_cloud_error.check_exc(exc) from None


def list_shared_with(uri):
    """Return array sharing policies"""
    (namespace, array_name) = split_uri(uri)
    api_instance = client.client.array_api

    try:
        return api_instance.get_array_sharing_policies(
            namespace=namespace, array=array_name
        )
    except GenApiException as exc:
        raise tiledb_cloud_error.check_exc(exc) from None


def share_array(uri, namespace, permissions):
    """
    Shares array with give namespace and permissions

    :param str namespace:
    :param list(str) permissions:
    :return:
    """

    if not isinstance(permissions, list):
        permissions = [permissions]

    for perm in permissions:
        if (
            not perm.lower() == rest_api.models.ArrayActions.READ
            and not perm.lower() == rest_api.models.ArrayActions.WRITE
        ):
            raise Exception("Only read or write permissions are accepted")

    (array_namespace, array_name) = split_uri(uri)
    api_instance = client.client.array_api

    try:
        return api_instance.share_array(
            namespace=array_namespace,
            array=array_name,
            array_sharing=rest_api.models.ArraySharing(
                namespace=namespace, actions=permissions
            ),
        )
    except GenApiException as exc:
        raise tiledb_cloud_error.check_exc(exc) from None


def unshare_array(uri, namespace):
    """
    Removes sharing of an array from given namespace

    :param str namespace: namespace to remove shared access to the array
    :return:
    :raises: :py:exc:
    """
    return share_array(uri, namespace, list())


def update_info(
    uri,
    array_name=None,
    description=None,
    access_credentials_name=None,
    tags=None,
):
    """
    Update an array's info
    :param str namespace: optional username or organization array should be registered under. If unset will default to the user
    :param str array_name: name of array to rename to
    :param str description: optional description
    :param str access_credentials_name: optional name of access credentials to use, if left blank default for namespace will be used
    :param list tags to update to
    """
    api_instance = client.client.array_api
    (namespace, current_array_name) = split_uri(uri)

    try:
        return api_instance.update_array_metadata(
            namespace=namespace,
            array=current_array_name,
            array_metadata=rest_api.models.ArrayInfoUpdate(
                description=description,
                name=array_name,
                uri=uri,
                access_credentials_name=access_credentials_name,
                tags=tags,
            ),
        )
    except GenApiException as exc:
        raise tiledb_cloud_error.check_exc(exc) from None


def register_array(
    uri, namespace=None, array_name=None, description=None, access_credentials_name=None
):
    """
    Register this array with the tiledb cloud service
    :param str namespace: optional username or organization array should be registered under. If unset will default to the user
    :param str array_name: name of array
    :param str description: optional description
    :param str access_credentials_name: optional name of access credentials to use, if left blank default for namespace will be used
    """
    api_instance = client.client.array_api

    if namespace is None:
        if config.user is None:
            config.user = client.user_profile()

        namespace = config.user.username

    try:
        return api_instance.register_array(
            namespace=namespace,
            array=uri,
            array_metadata=rest_api.models.ArrayInfoUpdate(
                description=description,
                name=array_name,
                uri=uri,
                access_credentials_name=access_credentials_name,
            ),
        )
    except GenApiException as exc:
        raise tiledb_cloud_error.check_exc(exc) from None


def deregister_array(uri):
    """
    Deregister the from the tiledb cloud service. This does not physically delete the array, it will remain
    in your bucket. All access to the array and cloud metadata will be removed.
    """
    (namespace, array_name) = split_uri(uri)

    api_instance = client.client.array_api

    try:
        return api_instance.deregister_array(namespace=namespace, array=array_name)
    except GenApiException as exc:
        raise tiledb_cloud_error.check_exc(exc) from None


def array_activity(uri):
    """
    Fetch array activity
    :param uri:
    :return:
    """
    (namespace, array_name) = split_uri(uri)

    api_instance = client.client.array_api

    try:
        return api_instance.array_activity_log(namespace=namespace, array=array_name)
    except GenApiException as exc:
        raise tiledb_cloud_error.check_exc(exc) from None


def split_uri(uri):
    """
    Split a URI into namespace and array name

    :param uri: uri to split into namespace and array name
    :return: tuple (namespace, array_name)
    """
    parsed = urllib.parse.urlparse(uri)
    if not parsed.scheme == "tiledb":
        raise Exception("Incorrect array uri, must be in tiledb:// scheme")
    return parsed.netloc, parsed.path[1:]


def parse_ranges(ranges):
    """
    Takes a list of the following objects per dimension:

    - scalar index
    - (start,end) tuple
    - list of either of the above types

    :param ranges: list of (scalar, tuple, list)
    :param builder: function taking arguments (dim_idx, start, end)
    :return:
    """

    def make_range(dim_range):
        if isinstance(dim_range, (int, float)):
            start, end = dim_range, dim_range
        elif isinstance(dim_range, (tuple, list)):
            start, end = dim_range[0], dim_range[1]
        elif isinstance(dim_range, slice):
            assert dim_range.step is None, "slice steps are not supported!"
            start, end = dim_range.start, dim_range.stop
        else:
            raise ValueError("Unknown index type! (type: '{}')".format(type(dim_range)))
        return [start, end]

    result = list()
    for dim_idx, dim_range in enumerate(ranges):
        dim_list = []
        # TODO handle numpy scalars here?
        if isinstance(dim_range, (int, float, tuple, slice)):
            dim_list.extend(make_range(dim_range))
        elif isinstance(dim_range, list):
            for r in dim_range:
                dim_list.extend(make_range(r))
        else:
            raise ValueError(
                "Unknown subarray/index type! (type: '{}', "
                ", idx: '{}', value: '{}')".format(type(dim_range), dim_idx, dim_range)
            )
        result.append(dim_list)

    return result


def apply_async(
    uri,
    func=None,
    ranges=None,
    name=None,
    attrs=None,
    layout=None,
    image_name=None,
    http_compressor="deflate",
    include_source_lines=True,
    task_name=None,
):
    """
    Apply a user defined function to an array asynchronous

    :param func: user function to run
    :param ranges: ranges to issue query on
    :param attrs: list of attributes or dimensions to fetch in query
    :param layout: tiledb query layout
    :param image_name: udf image name to use, useful for testing beta features
    :param http_compressor: set http compressor for results
    :param include_source_lines: disables sending sources lines of function along with udf
    :param str task_name: optional name to assign the task for logging and audit purposes
    :return: UDFResult object which is a future containing the results of the UDF

    **Example**
    >>> import tiledb, tiledb.cloud, numpy
    >>> def median(df):
    ...   return numpy.median(df["a"])
    >>> # Open the array then run the UDF
    >>> tiledb.cloud.array.apply_async("tiledb://TileDB-Inc/quickstart_dense", median, [(0,5), (0,5)], attrs=["a", "b", "c"]).get()
    2.0
    """

    (namespace, array_name) = split_uri(uri)
    api_instance = client.client.udf_api

    if func is not None and not callable(func):
        raise TypeError("func argument to `apply` must be callable!")
    elif func is None and name is None or name == "":
        raise TypeError("name argument to `apply` must be set if no function is passed")

    pickledUDF = None
    source_lines = None
    if func is not None:
        source_lines = utils.getsourcelines(func) if include_source_lines else None
        pickledUDF = cloudpickle.dumps(func, protocol=udf.tiledb_cloud_protocol)
        pickledUDF = base64.b64encode(pickledUDF).decode("ascii")

    ranges = parse_ranges(ranges)

    converted_layout = "row-major"

    if layout is None:
        converted_layout = "unordered"
    elif layout.upper() == "R":
        converted_layout = "row-major"
    elif layout.upper() == "C":
        converted_layout = "col-major"
    elif layout.upper() == "G":
        converted_layout = "global-order"

    ranges = rest_api.models.UDFRanges(layout=converted_layout, ranges=ranges)

    if image_name is None:
        image_name = "default"
    try:

        kwargs = {"_preload_content": False, "async_req": True}
        if http_compressor is not None:
            kwargs["accept_encoding"] = http_compressor

        udf_model = rest_api.models.UDF(
            language=rest_api.models.UDFLanguage.PYTHON,
            _exec=pickledUDF,
            ranges=ranges,
            buffers=attrs,
            version="{}.{}.{}".format(
                sys.version_info.major,
                sys.version_info.minor,
                sys.version_info.micro,
            ),
            image_name=image_name,
            task_name=task_name,
        )

        if pickledUDF is not None:
            udf_model._exec = pickledUDF
        elif name is not None:
            udf_model.udf_info_name = name

        if source_lines is not None:
            udf_model.exec_raw = source_lines

        # _preload_content must be set to false to avoid trying to decode binary data
        response = api_instance.submit_udf(
            namespace=namespace, array=array_name, udf=udf_model, **kwargs
        )

        return UDFResult(response)

    except GenApiException as exc:
        raise tiledb_cloud_error.check_sql_exc(exc) from None


def apply(
    uri,
    func=None,
    ranges=None,
    name=None,
    attrs=None,
    layout=None,
    image_name=None,
    http_compressor="deflate",
    task_name=None,
):
    """
    Apply a user defined function to an array synchronous

    :param func: user function to run
    :param ranges: ranges to issue query on
    :param attrs: list of attributes or dimensions to fetch in query
    :param layout: tiledb query layout
    :param image_name: udf image name to use, useful for testing beta features
    :param http_compressor: set http compressor for results
    :param str task_name: optional name to assign the task for logging and audit purposes
    :return: UDFResult object which is a future containing the results of the UDF

    **Example**
    >>> import tiledb, tiledb.cloud, numpy
    >>> def median(df):
    ...   return numpy.median(df["a"])
    >>> # Open the array then run the UDF
    >>> tiledb.cloud.array.apply("tiledb://TileDB-Inc/quickstart_dense", median, [(0,5), (0,5)], attrs=["a", "b", "c"])
    2.0
    """
    return apply_async(
        uri=uri,
        func=func,
        ranges=ranges,
        name=name,
        attrs=attrs,
        layout=layout,
        image_name=image_name,
        http_compressor=http_compressor,
        task_name=task_name,
    ).get()
