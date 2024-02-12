import json
import operator
import os
import uuid
from datetime import datetime
from pyspark.sql.functions import col, create_map, lit, regexp_replace, udf
from pyspark.sql.session import SparkSession
from pyspark.sql.streaming import StreamingQuery
from pyspark.sql.types import (
    BinaryType,
    ByteType,
    IntegerType,
    LongType,
    MapType,
    StringType,
    StructField,
    StructType,
)
from typing import Any

from dataclasses import dataclass
from itertools import chain

from common.schema_registry import schema_retriver
from common.transformation import avro_resolver

ACK_SCHEMA = StructType([
    StructField("year", IntegerType()),
    StructField("month", IntegerType()),
    StructField("ts", LongType()),
    StructField("errors", StringType())
])

@dataclass(init=False)
class ack_payload(object):
    def __init__(self):
        pass
    @property
    def payload(self):
        ack_columns = {
            "event_id": "event_id",
            "errors": "errors"
        }
        return ack_columns
    @payload.getter
    def expression(self):
        mapping_expr = create_map(list(chain(*(
            (lit(key), col(value)) for (key, value) in self.payload.items()
        ))))
        return mapping_expr


def processor(spark: SparkSession, producer_stream: StreamingQuery, is_parallel: bool, logger: Any) -> StreamingQuery:
    environment = os.getenv("ENVIRONMENT")
    logger.info("start process ")
    payload_expression = ack_payload().expression
    producer_stream = (
        producer_stream.withColumn("mapped_ack", payload_expression)
        .withColumn("key", col("transaction_id"))
    )
    producer_stream = producer_stream.withColumn("topic", regexp_replace(col("test"), "events", ""))
    schema_id, schema = schema_retriver.get_schema_registry(environment=environment, counterparty="")
    schema_id = spark.sparkContext.broadcast(schema_id)
    schema = spark.sparkContext.broadcast(schema)
    try:
        producer_stream = producer_stream.withColumn("value", avro_resolver.encode_to_avro(schema_id=schema_id.value, schema=schema.value)(col("mapped_ack")))
    except Exception as error:
        logger.error(f"Failed to process s")
    return producer_stream
