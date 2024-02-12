import json
import logging
import operator
import os
from typing import Any

import boto3
import botocore
import pandas
from botocore.exceptions import ClientError

from common.aws import connection

logger = logging.getLogger(__name__)


def get_schema_objects(bucket: str, prefix: str) -> list[dict[str, Any]]:
    output = []
    client = connection.get_client(service_name="s3")
    s3_paths = client.list_objects_v2(Bucket=bucket, Prefix=prefix)
    for s3_paths in s3_paths.get("Contents"):
        try:
            s3_key = s3_paths.get("Key")
            s3_object = client.get_object(Bucket=bucket, Key=s3_key)
            s3_body = s3_object.get("Body").read().decode("utf-8")
            s3_key = s3_key.split("/", 1)[-1]
            output.append({"subject": s3_key, "body": json.loads(s3_body)})
        except Exception as error:
            logger.error(f'Schema at {s3_key} is invalid')
            raise Exception(f'Schema at {s3_key} is invalid')
    return output


def get_schema_id(bucket: str, schema_id: tuple[str]) -> list[dict[str, Any]]:
    output = {}
    client = connection.get_client(service_name="s3")
    for _id in schema_id:
        s3_prefix = os.path.join("schema_id", _id, "schema.json")
        try:
            s3_object = client.get_object(Bucket=bucket, Key=s3_prefix)
            s3_body = s3_object.get("Body").read().decode("utf-8")
            output |= {_id: json.loads(s3_body)}
        except Exception:
            output |= {_id: False}
    return output


def get_object(bucket: str, key: str) -> botocore.response.StreamingBody:
    client = connection.get_client(service_name="s3")
    try:
        s3_object = client.get_object(Bucket=bucket, Key=key)
    except botocore.exceptions.ClientError as error:
        logger.info(f'Failed to get object in s3 because of {error}')
        raise
    return s3_object.get("Body")
