import logging
import pyspark
from functools import lru_cache
from pyspark.sql.functions import col, lit
from pyspark.sql.session import SparkSession
from typing import Any

from common.transformation import avro_resolver

logger = logging.getLogger(__name__)


def describe_table(tablename: str, spark: SparkSession) -> dict[str, str]:
    try:
        desc_sql = f"DESCRIBE TABLE {tablename}"
        desc_table = spark.sql(desc_sql)
        description_info = [row.asDict() for row in desc_table.collect()]
    except Exception as error:
        raise error
    return {
        desc.get("col_name"): desc.get("data_type")
        for desc in description_info if desc.get("data_type") and not desc.get("col_name").startswith("Part")
    }


def table_meta(spark: SparkSession, landing_zone: dict[str, Any]) -> tuple[dict[str, str], str]:
    catalog = spark.conf.get("spark.sql.defaultCatalog")
    table_name = landing_zone.get("destination")
    destination_table = f"{catalog}.{table_name}"
    try:
        table_metadata = describe_table(tablename=destination_table, spark=spark)
    except Exception as error:
        logger.error(f"Destination table don't exists {error} exits")
        raise error
    return table_metadata, destination_table


def processor(spark: SparkSession,
              df: pyspark.sql.DataFrame,
              configuration_set: dict[str, Any],
              logger=logger) -> pyspark.sql.streaming.StreamingQuery:
    landing_zone = configuration_set.get("landing_zone")
    destination = landing_zone.get("destination")
    columns = landing_zone.get("columns")
    checkpoint_location = configuration_set.get("checkpoint_location")
    processing_time = configuration_set.get("processing_time")
    try:
        table_metadata, destination_table = table_meta(spark=spark, landing_zone=landing_zone)
    except Exception as error:
        logger.error(f"Failed to connect to iceberg {destination_table} {error}")
        raise error
    df = avro_resolver.processor(spark=spark, df=df, logger=logger)
    df = df.withColumn("processed", lit(False))
    for (column, data_type) in table_metadata.items():
        try:
            df = df.withColumn(column, col(column).cast(data_type))
        except Exception as error:
            raise Exception(f'Couldnt cast {column} to {data_type} for table with metadata {table_metadata}')
    return (
        df
        .select(columns)
        .writeStream
        .outputMode("append")
        .format("iceberg")
        .trigger(processingTime=processing_time)
        .option("checkpointLocation", checkpoint_location)
        .toTable(destination_table)
    )
