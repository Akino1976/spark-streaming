import logging
import operator
import os
from pyspark.sql.session import SparkSession
from pyspark.sql.streaming import StreamingQuery
from typing import Any

import common.aws.ssm as ssm

logger = logging.getLogger("GlueLogger")


def processor(spark: SparkSession,
              producer_stream: StreamingQuery,
              configuration_set: dict[str, Any],
              logger: Any) -> StreamingQuery:
    kafka_options = configuration_set.get("kafka")
    checkpoint_location = configuration_set.get("checkpoint_location")
    processing_time = configuration_set.get("processing_time")
    if operator.contains(["staging", "production"], os.getenv("ENVIRONMENT")):
        kafka_options = ssm.access_configuration(
            kafka_options=kafka_options,
            environment=os.getenv("ENVIRONMENT")
        )
    is_parallel = operator.contains(configuration_set.get("asset"), "parallel")
    producer_stream = ac.processor(spark=spark, producer_stream=producer_stream, is_parallel=is_parallel, logger=logger)
    return (
        producer_stream.select(["topic", "key", "value"])
            .writeStream
            .options(**kafka_options)
            .format("kafka")
            .option("checkpointLocation", checkpoint_location)
            .trigger(processingTime=processing_time)
            .start()
    )
