import logging
import os
from typing import Any

import config

import click

from aws import athena, glue, storage

logger = logging.getLogger(__name__)


@click.group()
def cli():
    pass


@cli.command()
def integration_handler():
    try:
        athena_processor = athena.processor()
    except Exception as error:
        logger.exception(f"Event not processed [{error}]")
        raise error
    logger.info(f"Successfully processed event {athena_processor}")
    return athena_processor


@cli.command()
def upload_handler():
    try:
        storage_processor = storage.processor()
    except Exception as error:
        logger.exception(f"Event not processed [{error}]")
        raise error
    logger.info(f"Successfully processed event {storage_processor}")
    return storage_processor


@cli.command()
def glue_handler():
    try:
        glue_processor = glue.processor()
    except Exception as error:
        logger.exception(f"Glue not processed [{error}]")
        raise error
    logger.info(f"Successfully processed event {glue_processor}")
    return glue_processor


if __name__ == "__main__":
    cli()
