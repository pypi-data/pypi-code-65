from typing import Union, List, Optional, Dict
import types

import pandas as pd
from datetime import datetime
from deprecated import deprecated
from requests.exceptions import HTTPError
from snowflake import connector as snowflake
from snowflake.connector import SnowflakeConnection
from snowflake.connector.pandas_tools import write_pandas

from pyrasgo.connection import Connection
from pyrasgo.feature import Feature, FeatureList
from pyrasgo.model import Model
from pyrasgo.member import Member
from pyrasgo.enums import Granularity, ModelType


class RasgoConnection(Connection):
    """
    Base connection object to handle interactions with the Rasgo API.

    Defaults to using the production Rasgo instance, which can be overwritten
    by specifying the `RASGO_DOMAIN` environment variable, eg:

    &> RASGO_DOMAIN=custom.rasgoml.com python
    >>> from pyrasgo import RasgoConnection
    >>> rasgo = Connection(api_key='not_a_key')
    >>> rasgo._hostname == 'custom.rasgoml.com'
    True

    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def create_model(self, name: str,
                     type: Union[str, ModelType],
                     granularity: Union[str, Granularity]) -> Model:
        """
        Creates model within Rasgo within the account specified by the API key.
        :param name: Model name
        :param model_type: Type of model specified
        :param granularity: Granularity of the data.
        :return: Model object.
        """
        self._note({'event_type': 'create_model'})
        try:
            # If not enum, convert to enum first.
            model_type = type.name
        except AttributeError:
            model_type = ModelType(type)

        try:
            # If not enum, convert to enum first.
            granularity = granularity.name
        except AttributeError:
            granularity = Granularity(granularity)

        # TODO: API should really have _some_ validation for the schema of this post.
        response = self._post("/models", _json={"name": name,
                                                "type": model_type.value,
                                                # TODO: This post should only be `granularity` for future compatibility
                                                #       Coordinate with API development to relax domain specificity
                                                "timeSeriesGranularity": granularity.value})
        return Model(api_key=self._api_key, api_object=response.json())

    def add_feature_to(self, model: Model, feature: Feature):
        model.add_feature(feature)

    def add_features_to(self, model: Model, features: FeatureList):
        model.add_features(features)

    def generate_training_data_for(self, model: Model):
        raise NotImplementedError

    def get_models(self) -> List[Model]:
        """
        Retrieves the list of models from Rasgo within the account specified by the API key.
        """
        self._note({'event_type': 'get_models'})
        response = self._get("/models", {"join": ["features", "author"],
                                         "filter": "isDeleted||$isnull"})
        return [Model(api_key=self._api_key, api_object=entry) for entry in response.json()]

    def get_model(self, model_id) -> Model:
        """
        Retrieves the specified model from Rasgo within the account specified by the API key.
        """
        self._note({'event_type': 'get_model', 'input': model_id})
        # TODO: The API should not throw a 500 if it can't find a non-existent model, it should return a 404
        try:
            self._get(f"/models/{model_id}")
        except HTTPError:
            # This assumes they've followed a work flow and had their API key verified (happens on class __init__).
            raise LookupError(f"The model (id={model_id}) could not be found in your Rasgo account.")
        # TODO: The API should not throw a 500 if it can't join against a non-existent model, it should return a 404.
        response = self._get(f"/models/{model_id}", {"join": ["features", "author"]})
        return Model(api_key=self._api_key, api_object=response.json())

    def get_feature(self, feature_id) -> Feature:
        """
        Retrieves the specified feature from Rasgo within the account specified by the API key.
        """
        self._note({'event_type': 'get_feature', 'input': feature_id})
        response = self._get(f"/features/{feature_id}")
        return Feature(api_key=self._api_key, api_object=response.json())

    def get_features(self) -> FeatureList:
        """
        Retrieves the features from Rasgo within account specified by the API key.
        """
        self._note({'event_type': 'get_features'})
        response = self._get("/features")
        return FeatureList(api_key=self._api_key, api_object=response.json())

    def get_features_for(self, model: Model) -> FeatureList:
        raise NotImplementedError()
        # self._note({'event_type': 'get_features_for'})
        # response = self._get("/features",
        #                      params={'join': f""})
        #                    # params={'filter': f"||eq||DateTime"})
        # return FeatureList(response.json())

    def get_feature_data(self, model_id: int,
                         filters: Optional[Dict[str, str]] = None,
                         limit: Optional[int] = None) -> pd.DataFrame:
        """
        Constructs the pandas dataframe for the specified model.

        :param model_id: int
        :param filters: dictionary providing columns as keys and the filtering values as values.
        :param limit: integer limit for number of rows returned
        :return: Dataframe containing feature data
        """
        self._note({'event_type': 'get_models'})
        model = self.get_model(model_id)

        conn, creds = self._snowflake_connection(model.get_author())

        table_metadata = model.snowflake_table_metadata(creds)
        query, values = self._make_select_statement(table_metadata, filters, limit)

        result_set = self._run_query(conn, query, values)
        return pd.DataFrame.from_records(iter(result_set), columns=[x[0] for x in result_set.description])

    def get_feature_sets(self):
        """
        Retrieves the feature sets from Rasgo within account specified by the API key.
        """
        self._note({'event_type': 'get_feature_sets'})
        response = self._get("/feature-sets")
        return response.json()

    def get_data_sources(self):
        """
        Retrieves the data sources from Rasgo within account specified by the API key.
        """
        self._note({'event_type': 'get_data_sources'})
        response = self._get("/data-source")
        return response.json()

    def get_dimensionalities(self):
        """
        Retrieves the data sources from Rasgo within account specified by the API key.
        """
        self._note({'event_type': 'get_dimensionalities'})
        response = self._get("/dimensionalities")
        return response.json()

    def get_datasource(self, name):
        rows = self.find("data-source", {"name": name})
        if 0 == len(rows):
            return None
        else:
            return rows[0]

    def get_member(self):
        user = self.get_user()
        return Member(user)

    def get_user(self):
        response = self._get("/users")
        response_body = response.json()
        user = response_body[0]
        return user

    def get_user_id(self):
        """
        Gets the user id for the API key provided, or None if not available.
        NOTE: This is used for monitoring/logging purposes.
        """
        if self._user_id:
            return self._user_id
        else:
            try:
                user = self.get_user()
                self._user_id = user.get('id')
                return self._user_id
            except Exception:
                return None            

    def post_featureset(self, name, datasource_id, table_name, granularity=None):
        if granularity is None:
            granularity = '' 
        feature_set = {
            "snowflakeTable": table_name,
            "name": name,
            "dataSource": {
                "id": datasource_id
                },
            "granularity": granularity
            }
        response = self._post("feature-sets", feature_set)
        response.raise_for_status()
        return response.json()

    def get_dimensionality(self, name):
        return self._get_item("dimensionalities", {"name": name}, True)

    def create_dimensionality(self, org_id, name, dimension_type, granularity):
        dimensionality = {
            "name": name,
            "dimensionType": dimension_type,
            "granularity": granularity,
            "organization": {
                "id": org_id,
                },
            }
        response = self._post("/dimensionalities", dimensionality)
        response.raise_for_status()
        return response.json()

    def create_column(self, name, data_type, feature_set_id, dimension_id):
        column = {
            "name": name,
            "dataType": data_type,
            "featureSet": {
                "id": feature_set_id,
                },
            "dimensionality": {
                "id": dimension_id
                }
            }
        response = self._post("/rcolumns", column)
        response.raise_for_status()
        return response.json()

    def create_feature(self, org_id, featureset_id, name, code, description, column_id):
        feature = {
            "name": name,
            "code": code,
            "description": description,
            "featureSet": {
                "id": featureset_id,
                },
            "column": {
                "id": column_id,
                },
            "organization": {
                "id": org_id
            }
            }
        response = self._post("/features", feature)
        response.raise_for_status()
        return response.json()

    def create_datasource(self, org_id, name):
        abbrev = name[:10].lower()
        data_source = {
            "name": name,
            "abbreviation": abbrev,
            "organization": {"id": org_id}
            }
        response = self._post("data-source", data_source)
        response.raise_for_status()
        return response.json()

    def dimensionality_name(self, datatype, granularity):
        return "{} - {}".format(datatype, str(granularity).title())

    def publish_dimensionality(self, org_id, dimension_type, granularity):
        """
        Dimensionality is a named pairing of a datatype and a granularity. Note in some cases the
        granularity is actually a data type.
        """
        if dimension_type is None:
            if granularity.lower() in ['hour','day','week','month','quarter','year']:
                dimension_type = 'DateTime'
            else:
                dimension_type = "Custom"
        elif dimension_type.lower() == "datetime":
            dimension_type = "DateTime"
        else:
            dimension_type = dimension_type.title()
        dimensionality_name = self.dimensionality_name(dimension_type, granularity)

        # Check for a 'dimensionality' record that corresponds to the the dimensions
        # datatype and granularity.
        dimensionality = self.get_dimensionality(dimensionality_name)
        if dimensionality:
            return dimensionality
        else:
            return self.create_dimensionality(org_id, dimensionality_name, dimension_type, granularity)

    def publish_dimension(self, org_id, featureset_id, name, data_type, dimension_type = None, granularity = None ):
        dimemnsionality = self.publish_dimensionality(org_id, dimension_type, granularity)
        dimemnsionality_id = dimemnsionality['id']
        return self.create_column(name, data_type, featureset_id, dimemnsionality_id)

    def publish_feature(self, org_id, featureset_id, name, data_type, code = None, description = None, granularity = None):
        if code is None:
            code = name
        if description is None:
            description = "Feature that contains {} data".format(name)
        if granularity is None:
            dimension_id = None
        else:
            dimemnsionality = self.publish_dimensionality(org_id, None, granularity)
            dimension_id = dimemnsionality['id']
        column = self.create_column(code, data_type, featureset_id, dimension_id)
        column_id = column['id']
        feature = self.create_feature(org_id, featureset_id, name, code, description, column_id)
        return feature

    def publish_datasource(self, org_id, ds_name):
        # Check for a 'dimensionality' record that corresponds to the the dimensions
        # datatype and granularity.
        ds = self.get_datasource(ds_name)
        if ds:
            return ds
        else:
            newds = self.create_datasource(org_id, ds_name)
            return newds

    def _confirm_df_columns(self, dataframe, dimensions, features):
        df_columns = list(dataframe.columns)
        missing_dims = []
        missing_features = []
        for dim in dimensions:
            if dim not in df_columns:
                missing_dims.append(dim)
        for ft in features:
            if ft not in df_columns:
                missing_features.append(ft)
        if missing_dims or missing_features:
            raise Exception("Specified columns do not exist in dataframe: Dimensions({}) Features({})".format(missing_dims, missing_features))

    def _generate_featureset_name(self, dimensions, timestamp):
        args = {
            "timestamp": timestamp,
            "dimensions": "-".join(dimensions),
            }
        return "pandas_by_{dimensions}_{timestamp}".format(**args)

    def _snowflakify_name(self, name):
        '''
        param name: string
        return: string
        Converts a string to a snowflake compliant value
        Removes double quotes, replaces dashes with underscores, casts to upper case
        '''
        name = name.replace("-", "_")
        name = name.replace('"','')
        return name.upper()

    def _snowflakify_list(self, list_in):
        '''
        param list_in: list
        return list_out: list
        Changes a list of columns to Snowflake compliant names
        '''
        list_out = [self._snowflakify_name(n) for n in list_in]
        return list_out

    def _snowflakify_dataframe(self, dataframe: pd.DataFrame):
        '''
        param dataframe: dataframe holding columns
        param column: list of column names that need to change
        Renames all columns in a pandas dataframe to Snowflake compliant names
        '''
        schema = self._schema_for_dataframe(dataframe)
        cols = {}
        for r in schema:
            oldc = r
            newc = self._snowflakify_name(oldc)
            cols[oldc] = newc
        dataframe.rename(columns=cols,inplace=True)

    def _dataframe_to_snowflake(self, dataframe, table_name):
        #establish SF connection
        conn, creds = self._snowflake_connection(self.get_member())
        with conn.cursor() as cur:
            #Create the table in Snowflake
            tablesql = self._generate_ddl_from_dataframe(dataframe, table_name)
            cur.execute(tablesql)
            #Grant access to all Rasgo roles
            grantsql = f'GRANT SELECT ON TABLE {table_name} TO ROLE RASGO'
            cur.execute(grantsql)
        #load data from df to SF table
        write_pandas(conn, dataframe, table_name)

    def _generate_ddl_from_dataframe(self, df, table_name):
        sql_text = pd.io.sql.get_schema(df.reset_index(), table_name) 
        sql_text = sql_text.replace('CREATE TABLE','CREATE OR REPLACE TABLE')
        sql_text = sql_text.replace('"','')
        return sql_text

    def _schema_for_dataframe(self, df):
        from pandas.io.json import build_table_schema
        schema_list = build_table_schema(df)
        schema = {}
        for column in schema_list['fields']:
            name = column['name']
            schema[name] = column
        return schema
    
    def publish_features_from_df(self, dataframe, dimensions, features, granularity=None):
        # todo: Optionally generate list of feature columns from the dataframe columns, ie - all non-dimensions are features
        # todo: Add option to specify a featureset name + add check that it exists.
        self._note({'event_type': 'publish_features_from_df'})
        member = self.get_member()
        org_id = member.organization_id()
        now = datetime.now()
        timestamp = now.strftime("%Y_%m_%d_%H_%M")

        # Look up the DataSource as we need it's ID, and we also want to confirm it exists.
        datasource_name = 'PANDAS'
        data_source = self.publish_datasource(org_id, datasource_name)

        #Convert all strings to work with Snowflake
        dimensions = self._snowflakify_list(dimensions)
        features = self._snowflakify_list(features)
        self._snowflakify_dataframe(dataframe)

        # Confirm each named dimension and feature exists in the dataframe.
        self._confirm_df_columns(dataframe, dimensions, features)

        # Generate featureset name.
        featureset_name = self._generate_featureset_name(dimensions, timestamp)
        
        # Create a table in Snowflake with the subset of columns we're interested in, name table after featureset.
        all_columns = dimensions + features
        exportable_df = dataframe[all_columns]
        table_name = self._snowflakify_name(featureset_name)
        self._dataframe_to_snowflake(exportable_df, table_name)

        # Add a reference to the FeatureSet
        featureset_name = table_name
        datasource_id = data_source["id"]
        featureset = self.post_featureset(featureset_name, datasource_id, table_name, granularity)
        featureset_id = featureset["id"]
        schema = self._schema_for_dataframe(dataframe)

        # Add references to all the dimensions
        for d in dimensions:
            column = schema[d]
            data_type = column['type']
            dimension_name = column['name']
            self.publish_dimension(org_id, featureset_id, dimension_name, data_type, None, granularity)

        # Add references to all the features
        for f in features:
            column = schema[f]
            data_type = column['type']
            code = column['name']
            feature_name = "PANDAS_{col}_{ts}".format(col = code, ts = timestamp)
            self.publish_feature(org_id, featureset_id, feature_name, data_type, code, None, granularity)

        return featureset

    def publish_features_from_yml(self):
        raise NotImplementedError('Method not yet available through pyRasgo')

    def _note(self, event_dict: dict) -> None:
        """
        Emit event to monitoring service.
        :param event_dict: Dictionary containing desired attributes to emit.
        :return:
        """
        _event = 'pyrasgo: {}'.format(event_dict['event_type'])
        _properties = self._event_properties
        if 'input' in event_dict:
            _properties['input'] = event_dict['input']
        self._event_logger.track(
            identity=self._user_id,
            event=_event,
            properties=_properties
        )

    @staticmethod
    def _snowflake_connection(member) -> (SnowflakeConnection, dict):
        """
        Constructs connection object for Snowflake data platform
        :param member: credentials for Snowflake data platform

        :return: Connection object to use for query execution
        """
        creds = member.snowflake_creds()
        conn = snowflake.connect(**creds)
        return conn, creds

    @staticmethod
    def _make_select_statement(table_metadata, filters, limit) -> tuple:
        """
        Constructs select * query for table
        """
        query = "SELECT * FROM {database}.{schema}.{table}".format(**table_metadata)
        values = []
        if filters:
            comparisons = []
            for k, v in filters.items():
                if isinstance(v, list):
                    comparisons.append(f"{k} IN ({', '.join(['%s']*len(v))})")
                    values += v
                else:
                    comparisons.append(f"{k}=%s")
                    values.append(v)
            query += " WHERE " + " and ".join(comparisons)
        if limit:
            query += " LIMIT {}".format(limit)
        return query, values

    @staticmethod
    def _run_query(conn, query: str, params):
        """
        Execute a query on the [cloud] data platform.

        :param conn: TODO -> abstract the cloud data platform connection
        :param query: String to be executed on the data platform
        :return:
        """
        return conn.cursor().execute(query, params)

    @deprecated("This function has been deprecated, use `get_models` instead.")
    def get_lists(self) -> List[Model]:
        """
        Deprecated function.  Renamed to `get_models.`
        """
        self._note({'event_type': 'get_lists'})
        return self.get_models()

    @deprecated("This function has been deprecated, use `get_model` instead.")
    def get_feature_list(self, list_id) -> Model:
        """
        Deprecated function.  Renamed to `get_model.`
        """
        self._note({'event_type': 'get_feature_list'})
        return self.get_model(model_id=list_id)
