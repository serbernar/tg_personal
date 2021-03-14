from os import getenv
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(".")

ENV_FILE = getenv("ENV_FILE", ".env")
load_dotenv(ENV_FILE)

API_ID = int(getenv("API_ID"))
API_HASH = getenv("API_HASH")
USERNAME = getenv("USERNAME", "")
DATA_DIR = Path(BASE_DIR, "data", USERNAME)
