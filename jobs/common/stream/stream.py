import logging
import operator
import os
import pyspark
from pyspark.sql.functions import col
from pyspark.sql.session import SparkSession
from pyspark.sql.streaming import StreamingQuery
from typing import Any

from common.transformation import avro_resolver

logger = logging.getLogger("GlueLogger")



def processor(spark: SparkSession,
              df: StreamingQuery,
              configuration_set: dict[str, Any],
              logger: Any) -> StreamingQuery:
    landing_zone = configuration_set.get("landing_zone")
    destination = landing_zone.get("destination")
    partitions = landing_zone.get("partition")
    columns = landing_zone.get("columns")
    checkpoint_location = configuration_set.get("checkpoint_location")
    processing_time = configuration_set.get("processing_time")
    df = avro_resolver.stream_processor(spark=spark, df=df, logger=logger)
    return (
        df
        .repartition(*partitions)
        .select(columns)
        .writeStream
        .format("parquet")
        .outputMode("append")
        .option("path", destination)
        .partitionBy(*partitions)
        .trigger(processingTime=processing_time)
        .option("checkpointLocation", checkpoint_location)
        .start()
    )
