#
"""
Adapted from
https://github.com/Pylons/pyramid_debugtoolbar/blob/master/pyramid_debugtoolbar/panels/sqla.py
https://github.com/qiajigou/flask-zipkin/blob/master/flask_zipkin.py
"""
from sqlalchemy import event
from sqlalchemy.engine.base import Engine
from sqlalchemy.engine.url import URL as sqa_URL

from py_zipkin.thread_local import get_zipkin_attrs
from py_zipkin.util import generate_random_64bit_string
from py_zipkin.zipkin import zipkin_client_span, create_attrs_for_span, ZipkinAttrs


"""
def http_transport(encoded_span):
    # The collector expects a thrift-encoded list of spans. Instead of
    # decoding and re-encoding the already thrift-encoded message, we can just
    # add header bytes that specify that what follows is a list of length 1.
    body = '\x0c\x00\x00\x00\x01' + encoded_span
    requests.post(
        'http://localhost:9411/api/v1/spans',
        data=body,
        headers={'Content-Type': 'application/x-thrift'},
    )
"""

ZIPKIN_THRIFT_PREAMBLE = '\x0c\x00\x00\x00\x01'.encode()


class SqlAlchemyZipkinInstrumentation(object):

    INFO_ZIPKIN_SPAN = 'zipkin_span'

    def __init__(self, transport_handler, sample_rate=100.0, max_length=4096):
        # type: (typing.Callable[[bytes], None], float) -> None
        self.sample_rate = sample_rate
        self.transport_handler = transport_handler
        self.max_length = max_length
        self.started = False

    def start(self):
        if self.started:
            return

        event.listen(Engine, 'before_cursor_execute', self.on_before_cursor_execute)
        event.listen(Engine, 'after_cursor_execute', self.on_after_cursor_execute)

    def stop(self):
        if not self.started:
            return

        event.remove(Engine, 'before_cursor_execute', self.on_before_cursor_execute)
        event.remove(Engine, 'after_cursor_execute', self.on_after_cursor_execute)

    def on_before_cursor_execute(self, conn, cursor, statement, parameters, context, executemany):
        """
        Setup instrumentation on DB connection for zipkin data

        :param sqlalchemy.engine.Connection conn: Connection object
        :param Any cursor: DBAPI cursor object
        :param str statement: string SQL statement, as to be passed to the DBAPI
        :param typing.Union[dict, tuple, list] parameters: Dictionary, tuple, or list of parameters being passed to
            the execute() or executemany() method of the DBAPI cursor. In some cases may be None.
        :param typing.Optional[sqlalchemy.engine.interfaces.ExecutionContext] context: ExecutionContext object in use.
            May be None.
        :param bool executemany: boolean, if True, this is an executemany() call, if False, this is an execute() call.
        """
        zipkin_attrs = get_zipkin_attrs()  # type: py_zipkin.zipkin.ZipkinAttrs
        """:type: py_zipkin.zipkin.ZipkinAttrs"""

        if zipkin_attrs:
            zipkin_attrs = ZipkinAttrs(
                trace_id=zipkin_attrs.trace_id,
                span_id=generate_random_64bit_string(),
                parent_span_id=zipkin_attrs.span_id,
                flags=zipkin_attrs.flags,
                is_sampled=zipkin_attrs.is_sampled,
            )

        else:
            zipkin_attrs = create_attrs_for_span(self.sample_rate)

        lower_statement = statement.lower().strip().split(' ', 1)
        operation = lower_statement[0]

        span = zipkin_client_span(
            service_name='sqlalchemy.{}'.format(conn.dialect.name),
            span_name=operation,
            transport_handler=self.transport_handler,
            sample_rate=self.sample_rate,
            zipkin_attrs=zipkin_attrs,
        )

        # We use a stack here for the occasional case where the cursor execute events may be nested.
        # http://docs.sqlalchemy.org/en/latest/faq/performance.html#query-profiling
        conn.info.setdefault(self.INFO_ZIPKIN_SPAN, []).append(span)
        span.start()

    def on_after_cursor_execute(self, conn, cursor, statement, parameters, context, executemany):
        """

        :param sqlalchemy.engine.Connection conn: Connection object
        :param Any cursor: DBAPI cursor object
        :param str statement: string SQL statement, as to be passed to the DBAPI
        :param typing.Union[dict, tuple, list] parameters: Dictionary, tuple, or list of parameters being passed to
            the execute() or executemany() method of the DBAPI cursor. In some cases may be None.
        :param typing.Optional[sqlalchemy.engine.interfaces.ExecutionContext] context: ExecutionContext object in use.
            May be None.
        :param bool executemany: boolean, if True, this is an executemany() call, if False, this is an execute() call.
        """
        # before cursor should always be called and it should match the number of times after is called.
        span = conn.info[self.INFO_ZIPKIN_SPAN].pop(-1)  # type: py_zipkin.zipkin.zipkin_span
        """:type: py_zipkin.zipkin.zipkin_span """

        # Create a safe version of connection url for logging (no credentials)
        url = conn.engine.url
        url = sqa_URL(drivername=url.drivername, host=url.host, port=url.port, database=url.database, query=url.query)

        lower_statement = statement.lower().strip().split(' ', 1)
        operation = lower_statement[0].lower()

        # TODO: Would be nice to lose data portion of statement only.
        if operation in ('insert', 'update'):
            statement = '<redacted>'
            parameters = ()

        # Add SQLAlchemy attributes to span before stopping it. Noop is sampling is not set or 0
        span.update_binary_annotations({
            'sql.engine.id': id(conn.engine),
            'sql.engine.url': str(url),
            'sql.statement': statement[:self.max_length],
            'sql.parameters': parameters,
        })

        span.stop()


__version__ = '0.2.0'
