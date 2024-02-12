import operator
import os
import pyspark
import sys
from pyspark import SparkConf, SparkContext
from pyspark.sql.session import SparkSession
from pyspark.sql.streaming import StreamingQuery
from typing import Any

from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.utils import getResolvedOptions

from common import settings, yaml
from common.stream import kafka_resolver
from common.transformation.acknowledgement import ACK_SCHEMA


def _load_spark(args: dict[str, str]) -> tuple[GlueContext, SparkSession, Job]:
    environment = os.getenv("ENVIRONMENT")
    region = os.getenv("REGION")
    conf_list = yaml.load_configuration(args=args, spark_conf="spark_producer_conf.yaml")
    spark_conf = SparkConf().setAll(conf_list)
    spark_context = SparkContext.getOrCreate(conf=spark_conf)
    spark_context.setLogLevel("INFO")
    glue_context = GlueContext(spark_context)
    job = Job(glue_context)
    job.init(args["JOB_NAME"], args)
    spark = SparkSession.builder.config(conf=spark_conf).getOrCreate()
    if operator.eq(environment, "docker"):
        hadoop_conf = spark.sparkContext._jsc.hadoopConfiguration()
        hadoop_conf.set("fs.s3a.endpoint", f"http://{settings.MOCK_AWS_HOST}")
        hadoop_conf.set("fs.s3.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
        hadoop_conf.set("com.amazonaws.services.s3.enableV4", "true")
        hadoop_conf.set("fs.s3a.connection.ssl.enable", "false")
        hadoop_conf.set("fs.s3a.path.style.access", "true")
        hadoop_conf.set("fs.s3a.aws.credentials.provider", "com.amazonaws.auth.profile.ProfileCredentialsProvider")
        hadoop_conf.set("fs.s3a.session.token", "token")
    return glue_context, spark, job


def _configuration(args: str) -> dict[str, Any]:
    yaml_file = args.get("asset")
    environment = os.getenv("ENVIRONMENT", args.get("environment"))
    configuration_file = f"{yaml_file}.yaml"
    if not os.path.exists(configuration_file):
        configuration_file = os.path.join("/home/glue_user/workspace", configuration_file)
    configuration_set = yaml.load_yaml(
        yaml_path=configuration_file,
        top_node=None
    )
    if operator.contains([*configuration_set], "__anchors__"):
        anchors = configuration_set.pop("__anchors__")
    if (kafka_options := configuration_set.get("kafka")) and isinstance(kafka_options, dict):
        kafka_options = kafka_options.get(environment)
        kafka_options["kafka.bootstrap.servers"] = ",".join(kafka_options.get("kafka.bootstrap.servers"))
        configuration_set |= {"kafka": kafka_options}
    if (processing_time := configuration_set.get("processing_time")) and isinstance(processing_time, dict):
        configuration_set |= {"processing_time": processing_time.get(environment)}
    return configuration_set | args


def _get_resolved_options(args: dict[str, str]):
    needed_parameters = ["--JOB_NAME", "TempDir", "--environment", "--region", "--asset"]
    if not all([operator.contains(needed_parameters, arg) for arg in sys.argv]):
        for (key, value) in args.items():
            sys.argv.append(f"--{key}")
            sys.argv.append(value)
    return getResolvedOptions(sys.argv, ["JOB_NAME", "TempDir", "environment", "region", "asset"])


def _test_progress(producer_stream: StreamingQuery) ->  bool:
    while True:
        recent_progress = producer_stream.recentProgress
        print(f"Progress {recent_progress}")
        logger.info(f"Progress {recent_progress}")
        if len(recent_progress) > 0:
            producer_stream.stop()
            break
    return True


def producer_streaming(spark: SparkSession, configuration_set: dict[str, Any], logger: Any):
    environment = os.getenv("ENVIRONMENT")
    is_test = operator.eq(environment, "docker")
    logger.info(f"Configuration {configuration_set}")
    load_path = configuration_set.get("load_path")
    producer_stream = (
        spark
        .readStream
        .format("parquet")
        .schema(ACK_SCHEMA)
        .load(load_path)
    )
    producer_stream = kafka_resolver.processor(
        spark=spark,
        producer_stream=producer_stream,
        configuration_set=configuration_set,
        logger=logger
    )
    if is_test: test_respons = _test_progress(producer_stream=producer_stream)
    producer_stream.awaitTermination()
    if not producer_stream.isActive and not is_test:
        logger.error(f"Streaming no longer active {configuration_set}")
        return False
    return True


if __name__ == "__main__":
    args = {"JOB_NAME": "local-test", "TempDir": "s3://global-resource-docker"} if operator.eq(settings.ENVIRONMENT, "docker") else {}
    args = _get_resolved_options(args=args)
    os.environ["ENVIRONMENT"] = args.get("environment")
    os.environ["REGION"] = args.get("region")
    os.environ["TEMPDIR"] = args.get("TempDir")
    setattr(settings, "REGION", args.get("region"))
    glue_context, spark, job = _load_spark(args=args)
    logger = glue_context.get_logger()
    logger.info(f"{spark.sparkContext._conf.getAll()}")
    configuration_set = _configuration(args=args)
    try:
        respons = producer_streaming(configuration_set=configuration_set, spark=spark, logger=logger)
    except Exception as error:
        logger.error(f"{error}")
    finally:
        job.commit()
        spark.stop()
