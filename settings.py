import logging.config
from os import getenv
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(".")

ENV_FILE = getenv("ENV_FILE", ".env")
load_dotenv(ENV_FILE)

DEBUG = getenv("DEBUG", False)

API_ID = 3472745
API_HASH = "5ecf99afe75faf6c60a4350cd56002e8"
USERNAME = getenv("USERNAME")
if not USERNAME:
    raise RuntimeError

DATABASE_URL = f"sqlite:///{USERNAME}.sqlite"

DATA_DIR = Path(BASE_DIR, "data", USERNAME)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {
        "standard": {"format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"},
    },
    "handlers": {
        "default": {
            "level": "INFO",
            "formatter": "standard",
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        "": {
            "handlers": ["default"],
            "level": "DEBUG" if DEBUG else "INFO",
            "propagate": False,
        },
        "telethon": {
            "handlers": ["default"],
            "level": "ERROR",
            "propagate": False,
        },
    },
}
logging.config.dictConfig(LOGGING)
