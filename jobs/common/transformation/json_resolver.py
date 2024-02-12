import base64
import collections
import json
import logging
import operator
import pyspark
from functools import reduce
from pyspark.sql.functions import (
    col,
    current_timestamp,
    date_format,
    lit,
    sha2,
    udf,
    unix_timestamp,
    year,
)
from pyspark.sql.session import DataFrame, SparkSession
from pyspark.sql.types import (
    BinaryType,
    ByteType,
    IntegerType,
    MapType,
    StringType,
)
from typing import Any

from common.transformation import utils

logger = logging.getLogger("GlueLogger")



def flatten(dictionary, parent_key="", separator="_"):
    """
    Flattens out nested dict, if list then stringify it
    """
    items = {}
    for key, value in dictionary.items():
        new_key = parent_key + separator + key if parent_key else key
        if isinstance(value, collections.abc.MutableMapping):
            items.update(flatten(value, new_key, separator))
        elif isinstance(value, list):
            items[new_key] = json.dumps(value) if value else None
        else:
            items[new_key] = value
    return items



@udf(returnType=StringType())
def encode_json(column: dict[str, Any]) -> str:
    return base64.b64encode(column).decode("ascii")


@udf(returnType=StringType())
def flatten_json(column: dict[str, Any]) -> str:
    flattened = flatten(json.loads(column))
    return bytearray(json.dumps(flattened).encode())


def udf_drop_event_keys(drop_event_keys: list[str]):
    return udf(lambda value: drop_event_keys_func(value, drop_event_keys), BinaryType())


def drop_event_keys_func(value: dict[str, Any], drop_keys=[]) -> dict[str, Any]:
    event = json.loads(value)
    for key in drop_keys:
        key_list = key.split('.')
        delete_key = key_list[-1]
        try:
            del reduce(operator.getitem, key_list[:-1], event)[delete_key]
        except KeyError:
            logger.info(f'Keypath {key_list} does not exist')
            pass
    flattened = flatten(event)
    return bytearray(json.dumps(flattened).encode())


def processor(spark: SparkSession, df: DataFrame, configuration_set: dict[str, Any], logger: Any) -> pyspark.sql.streaming.StreamingQuery:
    drop_event_keys = configuration_set.get("drop_event_keys")
    if drop_event_keys:
        df = df.withColumn("value", udf_drop_event_keys(drop_event_keys)(col("value")))
    else:
        df = df.withColumn("value", flatten_json(col("value")))
    df = (
        df.withColumn("kafka_metadata_schemaid", lit("json"))
        .withColumn("kafka_magic_byte", lit("json"))
        .withColumn("counterparty", utils.set_counterparty(col("topic")))
        .withColumn("kafka_metadata_kafka_ingested_timestamp", unix_timestamp(col("timestamp")))
        .withColumn("year", year(current_timestamp()))
        .withColumn("month", date_format(current_timestamp(), "MM"))
        .withColumn("ts", date_format(current_timestamp(), "yyyyMMddHH").cast(IntegerType()))
        .withColumn("key", col("key").cast("String"))
        .withColumnRenamed("topic", "kafka_metadata_topic")
        .withColumnRenamed("offset", "kafka_metadata_offset")
        .withColumnRenamed("partition", "kafka_metadata_partition")
    )
    df = (
        df.withColumn("kafka_metadata_hashed_payload", sha2((col("value")), 256))
        .withColumn("events", encode_json(col("value")))
    )
    logger.info(f"{df.printSchema()}")
    return df
