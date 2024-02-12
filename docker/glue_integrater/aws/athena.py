import logging
import operator
from time import sleep, time
from typing import Any, Dict, List

import config

import boto3

import aws.connection as connection

logger = logging.getLogger(__name__)


def get_workgroup_configuration(client: boto3.session.Session.client, workgroup: str) -> Dict[str, str]:
    try:
        workgroup_response = client.get_work_group(WorkGroup=workgroup)
        finance_wg = workgroup_response.get("WorkGroup")
    except Exception as error:
        raise error
    return {
        "name": finance_wg.get("Name"),
        "result_output": finance_wg.get("Configuration")["ResultConfiguration"]["OutputLocation"]
    }


def get_named_queries_id(client: boto3.session.Session.client, workgroup: str) -> List[str]:
    try:
        response = client.list_named_queries(MaxResults=50, WorkGroup=workgroup)
    except Exception as error:
        raise error
    return response.get("NamedQueryIds")


def _query_execution(client: boto3.session.Session.client, query_execution_id: str) -> bool:
    logger.info(f"check status for {query_execution_id}...")
    while True:
        sleep(20 - time() % 20)
        query_execution = client.get_query_execution(QueryExecutionId=query_execution_id)
        query_execution = query_execution.get("QueryExecution")
        status = query_execution.get("Status")["State"]
        if operator.contains(["FAILED", "CANCELLED"], status):
            failure_reason = query_execution.get("Status")['StateChangeReason']
            raise Exception(f"Could not query {query_execution_id} due to [{failure_reason}]")
        if operator.eq("SUCCEEDED", status):
            break
    logger.info(f"success for {query_execution_id}...")
    return True


def processor():
    client = connection.get_client(service_name="athena")
    logger.info("start athena query integration...")
    workgroup_configuration = get_workgroup_configuration(client=client, workgroup=f"finance-data-wg-{config.ENVIRONMENT}")
    queries_id = get_named_queries_id(client=client, workgroup=workgroup_configuration.get("name"))
    for query_id in queries_id:
        logger.info(f"running id {query_id}...")
        query_response = client.get_named_query(NamedQueryId=query_id)
        query_body = query_response.get("NamedQuery")
        query_response = client.start_query_execution(
            QueryString=query_body.get("QueryString"),
            QueryExecutionContext={
                "Database": query_body.get("Database"),
                "Catalog": "AwsDataCatalog"
            },
            WorkGroup=workgroup_configuration.get("name"),
            ResultConfiguration={
                "OutputLocation": workgroup_configuration.get("result_output"),
            }
        )
        query_status = _query_execution(client=client, query_execution_id=query_response.get("QueryExecutionId"))
    return query_status
