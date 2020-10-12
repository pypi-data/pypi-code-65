from typing import Dict
import boto3


def get_client(config: Dict[str, str]):
    """
    Get the appropriate client according to configuration sent.
    :param config: The config to get queues from aws, gcp or azure.
    :type config: dict
    :return: The appropriate client to get messages.
    """
    return boto3.client(
        "sqs",
        aws_access_key_id=config.get("aws_access_key_id"),
        aws_secret_access_key=config.get("aws_secret_access_key"),
        region_name=config["region_name"],
        endpoint_url="https://sqs.{}.amazonaws.com".format(config["region_name"])
    )
