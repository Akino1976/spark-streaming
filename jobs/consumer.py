import json
import operator
import os
import pyspark
import sys
from pyspark import SparkConf, SparkContext
from pyspark.sql.session import SparkSession
from typing import Any

from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.utils import getResolvedOptions

import common.aws.ssm as ssm
from common import settings, yaml
from common.stream import batch, stream


def _load_spark(args: dict[str, str]) -> tuple[GlueContext, SparkSession, Job]:
    environment = os.getenv("ENVIRONMENT")
    region = os.getenv("REGION")
    sink_operation = args.get("sink")
    conf_list = yaml.load_configuration(args=args, spark_conf="spark_conf.yaml")
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
        if kafka_options.get("subscribe"):
            kafka_options["subscribe"] = ",".join(kafka_options.get("subscribe"))
        kafka_options["kafka.bootstrap.servers"] = ",".join(kafka_options.get("kafka.bootstrap.servers"))
        configuration_set |= {"kafka": kafka_options}
    if (processing_time := configuration_set.get("processing_time")) and isinstance(processing_time, dict):
        configuration_set |= {"processing_time": processing_time.get(environment)}
    if (parallel_events := configuration_set.get("parallel_events")) and operator.contains(parallel_events.get("environment"), environment) :
        configuration_set |= {"parallel_events": parallel_events}
    return configuration_set | args


def _get_resolved_options(args: dict[str, str]):
    needed_parameters = ["--JOB_NAME", "TempDir", "--environment", "--region", "--asset" "--sink"]
    if not all([operator.contains(needed_parameters, arg) for arg in sys.argv]):
        for (key, value) in args.items():
            sys.argv.append(f"--{key}")
            sys.argv.append(value)
    return getResolvedOptions(sys.argv, ["JOB_NAME", "TempDir", "environment", "region", "asset", "sink"])


def _test_progress(write_stream: pyspark.sql.streaming.StreamingQuery) ->  bool:
    while True:
        recent_progress = write_stream.recentProgress
        print(f"Progress {recent_progress}")
        logger.info(f"Progress {recent_progress}")
        if len(recent_progress) > 0:
            write_stream.stop()
            break
    return True


PROCESSING = {
    "batch": batch.processor,
    "stream": stream.processor
}

def consumer_streaming(spark: SparkSession, configuration_set: dict[str, Any], logger: Any):
    is_test = operator.eq(os.getenv("ENVIRONMENT"), "docker")
    region = os.getenv("REGION")
    logger.info(f"Configuration {configuration_set}")
    kafka_options = configuration_set.get("kafka")
    sink = configuration_set.get("sink")
    if operator.contains(["staging", "production"], os.getenv("ENVIRONMENT")):
        kafka_options = ssm.access_configuration(
            kafka_options=kafka_options,
            environment=os.getenv("ENVIRONMENT")
        )
    df = (
        spark
        .readStream
        .format("kafka")
        .options(**kafka_options)
        .load()
    )
    processing_operation = PROCESSING.get(sink)
    write_stream = processing_operation(
        spark=spark,
        df=df,
        configuration_set=configuration_set,
        logger=logger
    )
    if is_test: test_respons = _test_progress(write_stream=write_stream)
    write_stream.awaitTermination()
    if not write_stream.isActive and not is_test:
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
        respons = consumer_streaming(configuration_set=configuration_set, spark=spark, logger=logger)
    except Exception as error:
        logger.error(f"{error}")
    finally:
        job.commit()
        spark.stop()
