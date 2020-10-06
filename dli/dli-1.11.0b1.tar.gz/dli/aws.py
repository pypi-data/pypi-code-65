#
# Copyright (C) 2020 IHS Markit.
# All Rights Reserved
#
import logging
import operator
import re
from datetime import timezone
from typing import Optional, List, Dict

from botocore.credentials import RefreshableCredentials
from botocore.session import get_session

from boto3 import Session
from dateutil.parser import isoparse

trace_logger = logging.getLogger('trace_logger')


class SplitString:
    """Field that serializes to a title case string and deserializes
    to a lower case string.
    """
    _re_match = re.compile(
        r'^([\sa-zA-z0-9_-]+)'
        '(<=|<|=|>|>=|!=)((?!<=|<|=|>|>=|!=)'
        r'[\sa-zA-z0-9_-]+)$'
    )

    def __init__(self, val):
        matches = SplitString._re_match.match(val)
        self.valid = True
        if not matches or len(matches.groups()) != 3:
            self.valid = False
            raise ValueError(
                f"Requested partition is invalid: {val}. Partition arguments "
                f"must be alphanumeric separated by an operator, and must "
                f"not be wrapped in special characters like single or double "
                f"quotations."
            )
        else:
            self.partition, self.operator, self.value = matches.groups()

    def as_dict(self):
        if self.valid:
            return {
                'partition': str(self.partition),
                'operator': str(self.operator),
                'value': str(self.value)
            }

        return None


def create_refreshing_session(
    dli_client_session, **kwargs
):
    """
    :param dli_client_session: We must not be closing over the original
    variable in a multi-threaded env as the state can become shared.
    :param kwargs:
    :return:
    """

    def refresh():
        auth_key = dli_client_session.auth_key
        expiry_time = dli_client_session.token_expires_on.replace(
            tzinfo=timezone.utc
        ).isoformat()

        return dict(
            access_key=auth_key,
            secret_key='noop',
            token='noop',
            expiry_time=expiry_time,
        )

    _refresh_meta = refresh()

    session_credentials = RefreshableCredentials.create_from_metadata(
        metadata=_refresh_meta,
        refresh_using=refresh,
        method='noop'
    )

    session = get_session()
    handler = kwargs.pop("event_hooks", None)
    if handler is not None:
        session.register(f'before-send.s3', handler)

    session._credentials = session_credentials
    return Session(
        botocore_session=session,
        **kwargs
    )


def _get_partitions_in_filepath(filepath: str) -> List[List[str]]:
    splits = filepath.split("/")
    return [x.split("=") for x in splits if "=" in x]


def _operator_lookup(op):
    return {
        '<': operator.lt,
        '>': operator.gt,
        '=': operator.eq,
        '<=': operator.le,
        '>=': operator.ge,
        '!=': operator.ne
    }[op]


def eval_logical(oper, field, val):
    return _operator_lookup(oper)(field, val)


def match_partitions(
    file_path: str,
    partitions: Optional[List[str]],
):
    # Convert from a list of string to a dictionary of partition, operator &
    # value
    query_partitions = [
        potential.as_dict() for potential in
        [
            SplitString(x)
            for x in partitions
        ] if potential.valid
    ]

    return _meets_partition_params(file_path, query_partitions)


def _meets_partition_params(
    file_path: str,
    query_partitions: Optional[List[Dict[str, str]]],
):
    # Copied from Consumption

    if query_partitions is None:
        return True

    # Convert Lists of List to Dictionary using dictionary comprehension.
    found_partitions = {
        x[0]: x[1] for x in _get_partitions_in_filepath(file_path)
    }

    filtered = [
        x for x in query_partitions
        if x['partition'] in found_partitions
    ]

    # Example:
    # found_p = dict[(k,v), (k1,v1)] = k:v, k1:v1
    # query_p = [{'partition':'date', 'operator':'<', 'value':'20190102'}]

    for filterable in filtered:
        field = filterable['partition']
        compare_val = found_partitions[field]
        op = filterable['operator']
        filter_value = filterable['value']

        if field == 'as_of_date':
            try:
                filter_value_date = isoparse(filter_value)
            except ValueError as e:
                # This means a user has given an invalid date
                raise ValueError(
                    'Was unable to parse the filter value you provided for '
                    'the `as_of_date` into a Python datetime: '
                    f"'{filter_value}'"
                ) from e

            try:
                compare_val = isoparse(compare_val)
            except ValueError:
                # Can not meet partition params as it not a date
                trace_logger.warning(
                    f'{file_path} is not a valid date.',
                    extra={
                        'file_path': file_path,
                        'filterable': filterable
                    },
                    exc_info=True
                )

                return False

            filter_value = filter_value_date

        match = eval_logical(
            op,
            field=compare_val,
            val=filter_value
        )

        if not match:
            # Short circuit as soon as we fail to match a filter.
            trace_logger.debug(
                f"Excluding file with path '{file_path}' because it "
                f"contains the partitions '{found_partitions}' and the "
                f"user is filtering with '{field}{op}{filter_value}' "
                f"which for this path is {compare_val}'."
            )
            return False

    not_filtered = [
        x for x in query_partitions
        if not x['partition'] in found_partitions
    ]

    if not_filtered:
        trace_logger.warning(
            f"These query partitions '{not_filtered}' were not found as "
            f"keys in the S3 path '{file_path}', so we are going to "
            'let this file through the filter but either the user has '
            'supplied an partition that does not exist or one of the S3 '
            'paths does not follow the partition pattern of the first S3 '
            'path in this instance.'
        )

    return True
