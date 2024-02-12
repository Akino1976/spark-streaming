import base64
import codecs
import io
import json
import logging
import operator
import os
import pyspark
from pyspark.sql.functions import (
    col,
    conv,
    current_timestamp,
    date_format,
    hex,
    substring,
    udf,
    unix_timestamp,
    year,
)
from pyspark.sql.session import DataFrame, SparkSession
from pyspark.sql.streaming import StreamingQuery
from pyspark.sql.types import (
    BinaryType,
    BooleanType,
    ByteType,
    IntegerType,
    MapType,
    StringType,
)
from struct import pack, unpack
from typing import Any

import fastavro
from cachetools import cached

from common.schema_registry import schema_retriver
from common.transformation import json_resolver, utils

logger = logging.getLogger("GlueLogger")


@udf(returnType=StringType())
def b64encode_dict(column: dict[str, Any]) -> str:
    try:
        payload = json.dumps(column).encode("ascii")
    except Exception:
        return -1
    return base64.b64encode(payload).decode("ascii")


class _ContextStringIO(io.BytesIO):
    """
        Wrapper to allow use of StringIO via 'with' constructs.
    """
    def __enter__(self):
        return self
    def __exit__(self, *args):
        self.close()
        return False


def avro_loader(column: dict[str, Any], schema_id: pyspark.broadcast.Broadcast, schema: pyspark.broadcast.Broadcast):
    parsed_schema = fastavro.parse_schema(schema)
    with _ContextStringIO() as fo:
        fo.write(pack('>bI', 0, schema_id))
        fastavro.schemaless_writer(fo, parsed_schema, column)
        return fo.getvalue()


def encode_to_avro(schema_id: pyspark.broadcast.Broadcast, schema: pyspark.broadcast.Broadcast):
    return udf(lambda column: avro_loader(column=column, schema_id=schema_id, schema=schema), BinaryType())



def parse_avro(column: str, schema_id: str, avro_schemas: dict[str, str]) -> dict[str, Any]:
    payload = codecs.decode(column, "hex_codec")
    try:
        schema_parsed = avro_schemas.get(schema_id)
        bytes_io = io.BytesIO(payload)
        bytes_io.seek(5)
        parsed_event = fastavro.schemaless_reader(bytes_io, schema_parsed)
        if isinstance(parsed_event, dict):
            return json_resolver.flatten(parsed_event)
    except Exception:
        return {schema_id: -1}


def decode_avro(avro_schemas_broadcasted: pyspark.broadcast.Broadcast):
    """
    USAGE: Function to utilize broadcast variables.
    """
    return udf(
        lambda column, schema_id: parse_avro(column, schema_id, avro_schemas_broadcasted),
        MapType(StringType(), StringType()),
    )


@udf(returnType=StringType())
def encode_avro(column: str) -> str:
    try:
        payload = codecs.decode(column, "hex_codec")
    except Exception:
        return -1
    return base64.b64encode(payload).decode("utf-8")


def batch_processor(spark: SparkSession, df: StreamingQuery, configuration_set: dict[str, Any], logger: Any) -> StreamingQuery:
    df = (
        df.withColumn("kafka_metadata_schemaid", conv(hex(substring(col("value"), 2, 4)), 16, 10))
        .withColumn("kafka_magic_byte", conv(hex(substring(col("value"), 1, 1)), 16, 10))
        .withColumn("counterparty", utils.set_counterparty(col("topic")))
        .withColumn("value", hex(col("value")))
        .withColumn("kafka_metadata_kafka_ingested_timestamp", unix_timestamp(col("timestamp")))
        .withColumn("year", year(current_timestamp()))
        .withColumn("month", date_format(current_timestamp(), "MM"))
        .withColumn("ts", date_format(current_timestamp(), "yyyyMMddHH").cast(IntegerType()))
        .withColumn("key", col("key").cast(StringType()))
        .withColumnRenamed("topic", "kafka_metadata_topic")
        .withColumnRenamed("offset", "kafka_metadata_offset")
        .withColumnRenamed("partition", "kafka_metadata_partition")
    )
    schemas_df = df.select("kafka_metadata_schemaid").distinct()
    schema_id = [str(row[0]) for row in schemas_df.select("kafka_metadata_schemaid").collect()]
    logger.info(f"Fetched {schema_id}")
    avro_schemas = schema_retriver.get_schema_s3(schema_id=tuple(schema_id))
    logger.info(f"Successfully extracted schemas {[*avro_schemas]}")
    avro_schemas_broadcasted = spark.sparkContext.broadcast(avro_schemas)
    df = (
        df.withColumn("events", decode_avro(avro_schemas_broadcasted.value)(col("value"), col("kafka_metadata_schemaid")))
        .withColumn("kafka_metadata_hashed_payload", encode_avro(col("value")))
        .withColumn("events", b64encode_dict(col("events")))
    )
    return df


def stream_processor(spark: SparkSession, df: StreamingQuery, logger: Any) -> StreamingQuery:
    avro_schemas = schema_retriver.get_schemas()
    avro_schemas_broadcasted = spark.sparkContext.broadcast(avro_schemas)
    df = (
        df.withColumn("kafka_metadata_schemaid", conv(hex(substring(col("value"), 2, 4)), 16, 10))
        .withColumn("kafka_magic_byte", conv(hex(substring(col("value"), 1, 1)), 16, 10))
        .withColumn("counterparty", utils.set_counterparty(col("topic")))
        .withColumn("value", hex(col("value")))
        .withColumn("kafka_metadata_kafka_ingested_timestamp", unix_timestamp(col("timestamp")))
        .withColumn("year", year(current_timestamp()))
        .withColumn("month", date_format(current_timestamp(), "MM"))
        .withColumn("ts", date_format(current_timestamp(), "yyyyMMddHH").cast(IntegerType()))
        .withColumn("key", col("key").cast(StringType()))
        .withColumnRenamed("topic", "kafka_metadata_topic")
        .withColumnRenamed("offset", "kafka_metadata_offset")
        .withColumnRenamed("partition", "kafka_metadata_partition")
    )
    df = (
        df.withColumn("events", decode_avro(avro_schemas_broadcasted.value)(col("value"), col("kafka_metadata_schemaid")))
        .withColumn("kafka_metadata_hashed_payload", encode_avro(col("value")))
        .withColumn("events", b64encode_dict(col("events")))
    )
    return df
