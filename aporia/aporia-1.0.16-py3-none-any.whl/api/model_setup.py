import logging
from typing import Dict, List, Optional, Tuple, Union

from aporia.consts import LOGGER_NAME
from aporia.graphql_client import GraphQLClient


logger = logging.getLogger(LOGGER_NAME)


async def check_model_exists(
    graphql_client: GraphQLClient, model_id: str, model_version: str, timeout: int
) -> Tuple[bool, bool]:
    """Checks if a model (and version) exists.

    Args:
        graphql_client (GraphQLClient): GraphQL client
        model_id (str): Model ID
        model_version (str): Model version
        timeout (int): Timeout for the query

    Returns:
        Tuple[bool, bool]: (model_exists, model_version_exists)
    """
    query = """
        query CheckModelExists(
            $modelId: String!,
            $modelVersion: String!
        ) {
            modelExists(
                modelId: $modelId,
                modelVersion: $modelVersion
            ) {
                modelExists
                modelVersionExists
            }
        }
    """
    variables = {
        "modelId": model_id,
        "modelVersion": model_version,
    }

    result = await graphql_client.query(query=query, variables=variables, timeout=timeout)
    result = result["modelExists"]
    return (result["modelExists"], result["modelVersionExists"])


async def set_features(
    graphql_client: GraphQLClient,
    model_id: str,
    model_version: str,
    feature_names: List[str],
    categorical_features: Optional[List[Union[int, str]]],
    timeout: int,
):
    """Sets model features.

    Args:
        graphql_client (GraphQLClient): GraphQL client
        model_id (str): Model ID
        model_version (str): Model version
        feature_names (List[str]): Feature names
        categorical_features (Optional[List[Union[int, str]]]): Categorical features
        timeout (int): Timeout for query
    """
    query = """
        mutation SetFeatures(
            $modelId: String!,
            $modelVersion: String!,
            $featureNames: [String]!,
            $categoricalFeatures: [FeatureDescriptor]
        ) {
            setFeatures(
                modelId: $modelId,
                modelVersion: $modelVersion,
                featureNames: $featureNames,
                categoricalFeatures: $categoricalFeatures
            ) {
                warnings
            }
        }
    """

    variables = {
        "modelId": model_id,
        "modelVersion": model_version,
        "featureNames": feature_names,
        "categoricalFeatures": categorical_features,
    }

    result = await graphql_client.query(query=query, variables=variables, timeout=timeout)
    for warning in result["setFeatures"]["warnings"]:
        logger.warning(warning)


async def add_extra_inputs(
    graphql_client: GraphQLClient,
    model_id: str,
    model_version: str,
    extra_inputs: Dict[str, str],
    timeout: int,
):
    """Defines extra inputs for the model.

    Args:
        graphql_client (GraphQLClient): GraphQL client
        model_id (str): Model ID
        model_version (str): Model version
        extra_inputs (Dict[str, str]): Extra inputs to define
        timeout (int): Timeout for the query
    """
    query = """
        mutation AddExtraInputs(
            $modelId: String!,
            $modelVersion: String!,
            $extraInputs: [ExtraInput]!,
        ) {
            addExtraInputs(
                modelId: $modelId,
                modelVersion: $modelVersion,
                extraInputs: $extraInputs,
            ) {
                warnings
            }
        }
    """

    variables = {
        "modelId": model_id,
        "modelVersion": model_version,
        "extraInputs": [
            {"name": input_name, "type": input_type.upper()}
            for input_name, input_type in extra_inputs.items()
        ],
    }

    result = await graphql_client.query(query=query, variables=variables, timeout=timeout)
    for warning in result["addExtraInputs"]["warnings"]:
        logger.warning(warning)


async def add_extra_outputs(
    graphql_client: GraphQLClient,
    model_id: str,
    model_version: str,
    extra_outputs: Dict[str, str],
    timeout: int,
):
    """Defines extra outputs for the model.

    Args:
        graphql_client (GraphQLClient): GraphQL client
        model_id (str): Model ID
        model_version (str): Model version
        extra_outputs (Dict[str, str]): Extra outputs to define
        timeout (int): Timeout for the query
    """
    query = """
            mutation AddExtraOutputs(
                $modelId: String!,
                $modelVersion: String!,
                $extraOutputs: [ExtraOutput]!,
            ) {
                addExtraOutputs(
                    modelId: $modelId,
                    modelVersion: $modelVersion,
                    extraOutputs: $extraOutputs,
                ) {
                    warnings
                }
            }
        """

    variables = {
        "modelId": model_id,
        "modelVersion": model_version,
        "extraOutputs": [
            {"name": output_name, "type": output_type.upper()}
            for output_name, output_type in extra_outputs.items()
        ],
    }

    result = await graphql_client.query(query=query, variables=variables, timeout=timeout)
    for warning in result["addExtraOutputs"]["warnings"]:
        logger.warning(warning)
