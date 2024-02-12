import contextlib
import logging
import operator
import time
from typing import Any

import config

import boto3

import aws.connection as connection

logger = logging.getLogger(__name__)

REGIONS = {
    "us-east-1": "us",
    "eu-west-1": "eu",
    "ap-southeast-2": "ap1"
}


def _get_id(client: boto3.session.Session.client, job_name: str) -> list[str]:
    response = client.get_job_runs(JobName=job_name)
    job_runs = response.get("JobRuns")
    job_ids = [
        job_run.get("Id") for job_run in job_runs
        if operator.eq(job_run.get("JobRunState"), "RUNNING")
    ]
    return job_ids


def _stop_and_run(client: boto3.session.Session.client,
                  job_name: str,
                  job_id: list[str]) -> dict[str, Any]:
    stop_response = client.batch_stop_job_run(JobName=job_name, JobRunIds=job_id)
    logger.info(f"Stopped {job_name}, {stop_response}")
    for i in range(0, 120):
        with contextlib.suppress(Exception):
            response = client.start_job_run(
                JobName=job_name,
                JobRunId=job_id[0]
            )
            if isinstance(response, dict):
                successful_submissions = response.get("SuccessfulSubmissions")
                logger.info("Succesfully started Glue {successful_submissions}")
                break
        time.sleep(5)
    return successful_submissions


def processor():
    response = False
    region = REGIONS.get(config.AWS_REGION)
    aws_region = config.AWS_REGION
    environment = config.ENVIRONMENT
    if operator.eq(environment, "staging") and operator.eq(aws_region, "us-east-1"):
        setattr(config, "AWS_REGION", "eu-west-1")
    client = connection.get_client(service_name="glue")
    job_names = [
        f"finance-data_streaming_{environment}-{region}",
        f"finance-data_producer_{environment}-{region}",
        f"finance-data_parallel_producer_{environment}-{region}",
        f"finance-data_consumer_parallel_{environment}-{region}",
        f"finance-data_interim_flow_{environment}-{region}",
        f"finance-data_kred_streaming_{environment}-{region}",
        f"finance-data_kred_order_streaming_{environment}-{region}",
        f"finance-data_kred_communication_events_streaming_{environment}-{region}"
    ]
    for job_name in job_names:
        try:
            job_id = _get_id(client=client, job_name=job_name)
            if len(job_id) > 0:
                response = _stop_and_run(client=client, job_name=job_name, job_id=job_id)
        except Exception as error:
            logger.info(f"{job_name} failed {error}")
    return response
