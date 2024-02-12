import logging
import operator
import os
import pyspark
from pyspark.sql.functions import col
from pyspark.sql.session import SparkSession
from pyspark.sql.streaming import StreamingQuery
from typing import Any

from common.custom_resolvers import avro_drop_select_keys
from common.transformation import avro_resolver, json_resolver

logger = logging.getLogger("GlueLogger")


def write_parquet(spark: SparkSession,
                  df: StreamingQuery,
                  configuration_set: dict[str, Any],
                  logger: Any) -> bool:
    process = False
    landing_zone = configuration_set.get("landing_zone")
    logger.info(f"Start saving file to {landing_zone}")
    parallel_events = configuration_set.get("parallel_events", False)
    destination = landing_zone.get("destination")
    partition = landing_zone.get("partition")
    columns = landing_zone.get("columns")
    try:
        (
            df
            .repartition(*partition)
            .select(columns)
            .write.option("compression", "snappy")
            .mode("append")
            .partitionBy(*partition)
            .parquet(destination)
        )
        process = True
    except Exception as error:
        logger.info(f"Failed to save to {destination}")
        logger.error(f"Failed to save to {error}")
    logger.info(f"saved to {destination} [{process}]")
    return True


TRANSFORMATION_OPERATION = {
    "avro": avro_resolver.batch_processor,
    "json": json_resolver.processor,
    "avro_drop_select_keys": avro_drop_select_keys.processor
}


def sink_streams(spark: SparkSession, configuration_set: dict[str, Any], logger: Any):
    def _processor(df, batch_id):
        try:
            parameters = {
                "spark": spark,
                "df": df,
                "configuration_set": configuration_set,
                "logger": logger
            }
            event_type = configuration_set.get("event_type", "avro")
            transformation = TRANSFORMATION_OPERATION.get(event_type)
            df = transformation(**parameters)
            logger.info("start saving parquet")
            _ = write_parquet(
                spark=spark,
                df=df,
                configuration_set=configuration_set,
                logger=logger
            )
            df.unpersist()
        except Exception as error:
            logger.error(f"Failed to process events {error}")
    return _processor


def processor(spark: SparkSession,
              df: StreamingQuery,
              configuration_set: dict[str, Any],
              logger: Any) -> StreamingQuery:
    checkpoint_location = configuration_set.get("checkpoint_location")
    processing_time = configuration_set.get("processing_time")
    return (
        df
        .writeStream
        .outputMode("append")
        .trigger(processingTime=processing_time)
        .option("checkpointLocation", checkpoint_location)
        .foreachBatch(sink_streams(spark=spark, configuration_set=configuration_set, logger=logger))
        .start()
    )
