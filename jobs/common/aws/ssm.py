import logging
import os
from functools import lru_cache
from typing import Any

import botocore.config
from botocore.exceptions import ClientError

from common.aws import connection

logging.getLogger('botocore').setLevel(logging.CRITICAL)
logging.getLogger('boto3').setLevel(logging.CRITICAL)
logger = logging.getLogger(__name__)


@lru_cache()
def get_ssm_param_value(param_name: str) -> str:
    logger.info(f"Retrieving parameter: {param_name}")
    client = connection.get_client(service_name="ssm")
    try:
        response = client.get_parameter(Name=param_name, WithDecryption=True)
    except botocore.exceptions.ClientError as error:
        logger.error(error)
        raise
    return response["Parameter"]["Value"]


def access_configuration(kafka_options: dict[str, Any], environment: str) -> dict[str, Any]:
    region = os.getenv("REGION")
    username = kafka_options.get("kafka_user", "spark-streaming")
    sasl_password = get_ssm_param_value(param_name=f"//{username}/{region}")
    scram_conf = f"org.apache.kafka.common.security.scram.ScramLoginModule required username='{username}' password='{sasl_password}';"
    kafka_options |= {"kafka.sasl.jaas.config": scram_conf}
    return kafka_options
