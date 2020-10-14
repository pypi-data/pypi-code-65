import logging
import dill
import jinja2
import os
import base64
import tempfile

from enum import Enum
from teradataml.dataframe.dataframe import DataFrame


class DistMode(Enum):
    LOCAL = 1
    STO = 2
    # DOCKER = 3
    # RTO = 4


class DistDataFrame(DataFrame):
    def __init__(self, table_name=None,
                 index=True,
                 index_label=None,
                 query=None,
                 materialize=False,
                 dist_mode=DistMode.LOCAL,
                 sto_id=None):
        super().__init__(table_name=table_name, index=index, index_label=index_label, query=query,
                         materialize=materialize)
        self.logger = logging.getLogger(__name__)

        if dist_mode == DistMode.STO and not sto_id:
            raise Exception("You must set sto_id parameter when dist_mode is STO")

        self.sto_id = sto_id
        self.dist_mode = dist_mode

        self.template_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(searchpath=os.path.dirname(os.path.realpath(__file__))))

        self.types_mapping = {
            "INTEGER": "int",
            "FLOAT": "float",
            "BYTEINT": "bool",
            "TIMESTAMP": "datetime64",
            "VARCHAR": "str",
            "BLOB": "str",
            "CLOB": "str"
        }

    def map(self, fun, partition_by=None, returns=None):
        """A map function which can be used to apply some logic defined in the
        provided lambda to every row. The function is applied on a row by row
        basis in whatever partition the STO executes. This will be applied
        to the associated data frame.

        PARAMETERS:
            func: A function conforming to
                        lambda row: do_something(row)
                  The row argument is a pandas dataframe
            partition_by: The partition key(s) to use (comma separated)
            returns: Python dictionary ({column_name1: type_value1, ... column_nameN: type_valueN})
        RETURNS:
            DataFrame with the map operation applied

        EXAMPLES
            --------
            >>> from tdextensions.distributed import DistDataFrame
            >>>
            >>> data = DataFrame("my_table")
            >>>
            >>> data.map(lambda row: do_something(row))
            >>>
        """

        return self._invoke_transform_op(fun, transform_op="map", partition_by=partition_by, returns=returns)

    def map_partition(self, fun, partition_by=None, chunk=False, returns=None):
        """A map function which can be used to apply some logic defined in the
        provided lambda to every partition. The function is applied on the
        partition level. This will be applied to the associated data frame.

        PARAMETERS:
            func: A function conforming to
                        lambda partition: do_something(partition)
                  The partition argument is a pandas dataframe
                  Returns the result of the function applied on each row
            partition_by: Comma separated partition key(s) to use
            chunk: Should the partition data be chunked (default: False)
        RETURNS:
            DataFrame with the map operation applied

        EXAMPLES
            --------
            >>> from tdextensions.distributed import DistDataFrame
            >>>
            >>> data = DataFrame("my_table")
            >>>
            >>> data.map_partition(
            >>> 	lambda partition: do_something(partition)
            >>> 	partition_by="my_partition_col")
        """
        if chunk:
            raise NotImplementedError("Chunking not implemented yet")

        return self._invoke_transform_op(fun, transform_op="map_partition", partition_by=partition_by, returns=returns)

    def predict(self, fun, model_id, partition_by=None, chunk=False, returns=None):
        """A map function which can be used to apply some logic defined in the
        provided lambda to every partition. The function is applied on the
        partition level but can be chunked to provide more memory efficient
        usage and to work on for example large unbalanced partitions.

        PARAMETERS:
            func:  A function conforming to
                        lambda partition, model: my_predict_func(partition, model)
                  The partition argument is a pandas dataframe
                  The model argument is an unpickled model (based on model_id)
                  Returns the predictions
            model_id: The model id of the model to read and unpickel in the func
            partition_by: comma separated partition key(s) to use
            chunk: should the partition data be chunked (default: False)
            returns: Python dictionary ({column_name1: type_value1, ... column_nameN: type_valueN})
        RETURNS:
            DataFrame with the predictions
        EXAMPLES
            --------
            >>> from tdextensions.distributed import DistDataFrame
            >>>
            >>> data = DataFrame("my_table")
            >>>
            >>> def my_predict_func(partition, model)
            >>>		predictions = model.predict(partition)
            >>>
            >>>		return partition.id, predictions[0], predictions[1]
            >>>
            >>> scores = data.predict(
            >>> 	lambda partition, model: my_predict_func(partition, model),
            >>> 	model_id = "my_model_id"
            >>> 	partition_by="my_partition_col")
            >>>	scores
            id, prediction, confidence
            1, 	1, 			0.95
            2,  0,			0.9
        """
        if chunk:
            raise NotImplementedError("Chunking not implemented yet")

        return self._invoke_transform_op(fun, transform_op="predict", partition_by=partition_by, returns=returns, model_id=model_id)

    @staticmethod
    def _pandas_type_converter(types):
        converters = {}
        for i, type in enumerate(types):
            if type in ("float", "float32"):
                converters[i] = lambda x: float("".join(x.split()))
            elif type in ("int", "int32", "int64"):
                converters[i] = lambda x: int(float("".join(x.split())))
            elif type in ("str", "object"):
                converters[i] = lambda x: x
            else:
                raise Exception("Unknown type: {}".format(type))

        return converters

    def _invoke_transform_op(self, fun, transform_op, partition_by=None, returns=None, **kwargs):

        out_type = self.dtypes._column_names_and_types
        if returns:
            out_type = returns

        jinja_ctx = {
            "fun_base64": base64.b64encode(dill.dumps(fun, recurse=True)),
            "in_types_base64": base64.b64encode(dill.dumps(self.dtypes._column_names_and_types, recurse=True)),
            "out_types_base64": base64.b64encode(dill.dumps(out_type, recurse=True)),
            "converters_base64": base64.b64encode(dill.dumps(DistDataFrame._pandas_type_converter, recurse=True)),
            "transform_op": transform_op
        }

        template = self.template_env.get_template("wrappers/sto.j2")

        with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as fp:
            self.logger.info("Writing templated python to {}".format(fp.name))
            fp.write(template.render(jinja_ctx).encode())

        if self.dist_mode == DistMode.LOCAL:
            return self._invoke_local_op(fp.name, partition_by=partition_by, returns=returns)

        elif self.dist_mode == DistMode.STO:
            return self._invoke_sto_op(fp.name, partition_by=partition_by, returns=returns)

        else:
            raise NotImplementedError("Mode {} not implemented yet..".format(self.dist_mode))

    def _invoke_sto_op(self, tmp_py_file, partition_by=None, returns=None, **kwargs):

        if not returns:
            raise Exception("return information must be set for STO operations")

        returns_sql = ', '.join(["{} {}".format(col[0], col[1]) for col in returns])

        from teradataml.context.context import get_connection
        from teradataml.context.context import _get_current_databasename
        conn = get_connection()

        db_name = _get_current_databasename()

        conn.execute("SET SESSION SEARCHUIFDBPATH = {}".format(db_name))
        try:
            conn.execute("CALL SYSUIF.REMOVE_FILE('{}',1)".format(self.sto_id))
        except:
            # drops fail if it doesn't exist..
            pass
        conn.execute("CALL SYSUIF.INSTALL_FILE('{0}','{0}.py','cz!{1}')".format(self.sto_id, tmp_py_file))

        partition_by_sql = ""
        if partition_by:
            partition_by_sql = "PARTITION BY {}".format(partition_by)

        sql = """
        SELECT * FROM SCRIPT( ON (SELECT * FROM {0} ) {1}
                SCRIPT_COMMAND('python3 ./{2}/{3}.py')
                RETURNS ('{4}')
        )""".format(self._table_name, partition_by_sql, db_name, self.sto_id, returns_sql)

        return DataFrame(query=sql)

    def _invoke_local_op(self, tmp_py_file, partition_by=None, returns=None, **kwargs):
        from io import StringIO
        from subprocess import Popen, PIPE
        import pandas as pd

        def call_script(df, col_names, col_types):
            output = StringIO()
            df.to_csv(output, sep='\t', header=False, index=False)

            p = Popen(["python", tmp_py_file], stdin=PIPE, stdout=PIPE, stderr=PIPE)
            std_out, std_err = p.communicate(output.getvalue().encode())
            p.wait()

            if p.returncode != 0:
                raise Exception("Return code was {}. Reason {}".format(p.returncode, std_err.decode()))

            return pd.read_csv(StringIO(std_out.decode()), sep='\t', header=None, names=col_names,
                               index_col=False, iterator=False,
                               converters=DistDataFrame._pandas_type_converter(col_types))

        if returns:
            out_col_names = [col[0] for col in returns]

            def _parse_type(col_type):
                return col_type.upper().split("(")[0]

            out_col_types = [self.types_mapping[_parse_type(col[1])] for col in returns]
        else:
            self.logger.debug("Return types not specified so using same as input")

            out_col_names = [col[0] for col in self.dtypes._column_names_and_types]
            out_col_types = [col[1] for col in self.dtypes._column_names_and_types]

        if partition_by:
            partitioned = self.to_pandas().groupby(partition_by)

            dfs = [call_script(partition, out_col_names, out_col_types) for _, partition in partitioned]

            df = pd.concat(dfs)

        else:
            df = call_script(self.to_pandas(), out_col_names, out_col_types)

        return df
