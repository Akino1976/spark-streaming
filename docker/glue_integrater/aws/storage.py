import logging
import operator
import os
from glob import glob
from typing import Any, Dict, List

import config

import boto3
import botocore.config
from botocore.exceptions import ClientError

import aws.connection as connection

logger = logging.getLogger(__name__)
logging.getLogger("botocore").setLevel(logging.CRITICAL)
logging.getLogger("boto3").setLevel(logging.CRITICAL)


def _get_all_files(directory: str, file_regexp: str = "*") -> List[str]:
    if os.path.exists(directory) is False:
        raise Exception(f"Directory dont exists {directory}")
    else:
        all_files = [
            base_path for filepath in os.walk(directory)
            for base_path in glob(os.path.join(filepath[0], file_regexp))
            if os.path.isfile(base_path)
        ]
    return all_files


def _upload_file(file_path: str, bucket_name: str) -> str:
    client = connection.get_client(service_name="s3")
    s3_key = file_path.split("glue_packer/")[-1]
    logger.info(f'Starting file-upload to S3-bucket, with prefix: [{s3_key}]')
    try:
        client.upload_file(Filename=file_path, Bucket=bucket_name, Key=s3_key)
    except ClientError as error:
        logger.exception(f'Error in uploading file to S3 [{error}]')
        return False
    return s3_key


def processor():
    output = []
    glue_uploads = _get_all_files(directory="glue_packer")
    for glue_upload in glue_uploads:
        file_name = _upload_file(file_path=glue_upload, bucket_name=config.GLUE_BUCKET)
        output.append(file_name)
    return output
