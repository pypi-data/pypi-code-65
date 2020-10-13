import logging
from typing import Any, Dict, Optional, Union

from pandas import read_sql, DataFrame
from sqlalchemy import create_engine

from etlops.clients.sql import SQLClient


class SnowflakeClient(SQLClient):
    SUSPENDED_WAREHOUSE_STATUS = ("SUSPENDED", "SUSPENDING")
    USER_IDENTIFIER = "user"
    PASSWORD_IDENTIFIER = "password"
    ACCOUNT_IDENTIFIER = "account"
    INSECURE_MODE = "insecure_mode"
    WAREHOUSE = "WAREHOUSE"
    SUSPEND_COMMAND = "suspend"
    RESUME_COMMAND = "resume"

    def __init__(
        self,
        config: Optional[Union[Dict[str, Any], str]] = None,
        *,
        user: Optional[str] = None,
        password: Optional[str] = None,
        account: Optional[str] = None,
        insecure_mode: bool = False
    ):
        if isinstance(config, str):
            self.configuration_dict = self._load_configuration_file(config)
        elif isinstance(config, dict):
            self.configuration_dict = config
        elif config is None:
            self.configuration_dict = {
                self.USER_IDENTIFIER: user,
                self.PASSWORD_IDENTIFIER: password,
                self.ACCOUNT_IDENTIFIER: account,
                self.INSECURE_MODE: insecure_mode,
            }

        self.sql_alchemy_connection = None
        self.__set_sql_aqlchemy_engine()
        self.logger = logging.getLogger("SnowflakeClient")

    @classmethod
    def from_dict(cls, config: Dict[str, Any]) -> "SnowflakeClient":
        """
        Alternate constructor to create a `SnowflakeClient` from a
        dictionary.

        Args:
            - config (Dict[str, Any]): Mapping of arguments required
                to connect to Snowflake.

        Raises:
            - ValueError: If one of the required keys is not present.
        """
        required_keys = [
            cls.USER_IDENTIFIER,
            cls.PASSWORD_IDENTIFIER,
            cls.ACCOUNT_IDENTIFIER,
            cls.INSECURE_MODE,
        ]
        for required_key in required_keys:
            if required_key not in config.keys():
                raise ValueError(
                    "Required key {key} not found in configuration".format(
                        key=required_key
                    )
                )
        return cls(**config)

    def __set_sql_aqlchemy_engine(self):
        self.sql_alchemy_engine = create_engine(
            "snowflake://{user}:{password}@{account}/".format(
                user=self.configuration_dict[SnowflakeClient.USER_IDENTIFIER],
                password=self.configuration_dict[SnowflakeClient.PASSWORD_IDENTIFIER],
                account=self.configuration_dict[SnowflakeClient.ACCOUNT_IDENTIFIER],
            ),
            connect_args={
                "insecure_mode": self.configuration_dict[SnowflakeClient.INSECURE_MODE]
            },
        )

    def connect(self) -> None:
        self.sql_alchemy_connection = self.sql_alchemy_engine.connect()
        self.logger.info("Snowflake Connection Open")

    def disconnect(self):
        if not self.sql_alchemy_connection:
            self.logger.info("Not connected to Snowflake. Skipping disconnect.")
            return
        self.sql_alchemy_connection.close()
        self.logger.info("Snowflake Connection Closed")

    def switch_to(self, db_object: str, db_object_name: str) -> None:
        if db_object.upper() == SnowflakeClient.WAREHOUSE:
            self.alter_warehouse(warehouse=db_object_name, action="resume")
        switching_query = "USE {OBJECT} {OBJECT_NAME};".format(
            OBJECT=db_object, OBJECT_NAME=db_object_name
        )
        self.sql_alchemy_connection.execute(switching_query)
        self.logger.info(
            "Switched to {OBJECT} = {OBJECT_NAME} successfully".format(
                OBJECT=db_object, OBJECT_NAME=db_object_name
            )
        )

    def __check_warehouse_state(self, warehouse: str) -> str:
        warehouse = warehouse.upper()
        warehouse_state_dataframe = self.select_query(
            "SHOW WAREHOUSES LIKE '{WAREHOUSE}';".format(WAREHOUSE=warehouse)
        )
        warehouse_state = warehouse_state_dataframe.loc[
            warehouse_state_dataframe["name"] == warehouse, "state"
        ].values[0]
        return warehouse_state

    def dml_query(self, query_string: str) -> None:
        self.sql_alchemy_connection.execute(query_string)

    def select_query(self, query_string: str) -> DataFrame:
        return read_sql(query_string, con=self.sql_alchemy_connection)

    def alter_warehouse(self, warehouse: str, action: str) -> None:
        status = self.__check_warehouse_state(warehouse)
        if (
            action == SnowflakeClient.SUSPEND_COMMAND
            and status not in SnowflakeClient.SUSPENDED_WAREHOUSE_STATUS
        ):
            self.__alter_warehouse_query(warehouse, SnowflakeClient.SUSPEND_COMMAND)
        elif (
            action == SnowflakeClient.RESUME_COMMAND
            and status in SnowflakeClient.SUSPENDED_WAREHOUSE_STATUS
        ):
            self.__alter_warehouse_query(warehouse, SnowflakeClient.RESUME_COMMAND)

    def __alter_warehouse_query(self, warehouse: str, command: str):
        self.dml_query(
            "Alter warehouse {WAREHOUSE} {COMMAND};".format(
                WAREHOUSE=warehouse, COMMAND=command
            )
        )
