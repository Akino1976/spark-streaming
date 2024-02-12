import logging
import os
from logging.config import dictConfig

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
ENVIRONMENT = os.getenv("ENVIRONMENT")
APP_PATH = os.path.dirname(os.path.realpath(PROJECT_ROOT))
PROJECT = os.getenv("PROJECT")

logging_config = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default_formatter': {
            'format': '[%(levelname)s:%(asctime)s] %(message)s'
        },
    },
    'handlers': {
        'stream_handler': {
            'class': 'logging.StreamHandler',
            'formatter': 'default_formatter',
        },
    },
    'loggers': {
        'mylogger': {
            'handlers': ['stream_handler'],
            'level': 'INFO',
            'propagate': True
        }
    }
}
dictConfig(logging_config)

AWS_REGION = os.getenv("AWS_REGION")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_SESSION_TOKEN = os.getenv("AWS_SESSION_TOKEN")
AWS_PROFILE = os.getenv("AWS_PROFILE")
GLUE_BUCKET = os.getenv("GLUE_BUCKET")
