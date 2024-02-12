import logging
import os
from functools import lru_cache
from typing import Any

import boto3
import botocore.config
import config

logger = logging.getLogger(__name__)
logging.getLogger('botocore').setLevel(logging.CRITICAL)
logging.getLogger('boto3').setLevel(logging.CRITICAL)


@lru_cache()
def get_client(service_name: str) -> boto3.session.Session.client:
    proxy = os.getenv("MOCK_AWS_HOST")
    params = dict(
        service_name=service_name,
        region_name=config.AWS_REGION,
        config=botocore.config.Config(
            connect_timeout=180,
            read_timeout=180,
            retries={'max_attempts': 5}
        )
    )
    if proxy:
        params['use_ssl'] = proxy.startswith('https://')
        params['config'].proxies = {'http': proxy}
        params["endpoint_url"] = f"http://{proxy}"
    return boto3.client(**params)
