import json
import logging
import operator
import os
from collections.abc import Callable
from functools import lru_cache
from typing import Any

import avro
import botocore
import pandas

import common.aws.storage as storage

logger = logging.getLogger("GlueLogger")



@lru_cache(maxsize=128, typed=False)
def get_schema_s3(schema_id: tuple[str]) -> dict[str, Any]:
    temp_dir = os.getenv("TEMPDIR").strip("s3://")
    logger.info(f"start getting data from {temp_dir} {schema_id}")
    try:
        schemas = storage.get_schema_id(bucket=temp_dir, schema_id=schema_id)
    except Exception as error:
        raise error
    return schemas


@lru_cache(maxsize=16)
def get_schema(search_id: str) -> dict[str, Any] | bool:
    temp_dir = os.getenv("TEMPDIR").strip("s3://")
    key = os.path.join("schema_id", search_id, "schema.json")
    streamed_body = storage.get_object(bucket=temp_dir, key=key)
    if isinstance(streamed_body, botocore.response.StreamingBody):
        try:
            body = streamed_body.read().decode("utf-8")
            body = json.loads(body)
            output = {search_id: body}
        except Exception:
            return False
    return output


def get_schema_registry(counterparty: str, environment: str) -> tuple[int, dict[str, Any]]:
    output = {}
    schema_path = os.path.join("schema_registry", f"counterparty={counterparty}")
    schemas = storage.get_schema_objects(bucket=f"global-resource-{environment}", prefix=schema_path)
    schemas_df = pandas.DataFrame(schemas)
    schemas_df.loc[:, "major_version"] = schemas_df.subject.str.extract(r"major_version=v(.*)/minor_version.*", expand=False)
    schemas_df.loc[:, "minor_version"] = schemas_df.subject.str.extract(r"minor_version=(.*)/schema_id.*", expand=False)
    schemas_df.loc[:, "schema_id"] = schemas_df.subject.str.extract(r"schema_id=(.*)/schema.*", expand=False)
    schemas_df = schemas_df.loc[schemas_df.major_version == "2.2"]
    schemas_df["schema_id"] = schemas_df.schema_id.astype("int")
    schemas_df = schemas_df.loc[schemas_df.schema_id.idxmax(), ["schema_id", "body"]]
    return schemas_df.schema_id, schemas_df.body


@lru_cache(maxsize=16)
def get_schemas() -> dict[str, Any]:
    temp_dir = os.getenv("TEMPDIR").strip("s3://")
    try:
        schemas = storage.get_schema_objects(bucket=temp_dir, prefix="schema_id")
        schemas = {schema.get("subject").split("/")[0]: schema.get("body") for schema in schemas}
    except Exception as error:
        raise error
    return schemas
