from os import getenv
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(".")

ENV_FILE = getenv("ENV_FILE", ".env")
load_dotenv(ENV_FILE)

API_ID = 3472745
API_HASH = "5ecf99afe75faf6c60a4350cd56002e8"
USERNAME = getenv("USERNAME")
if not USERNAME:
    raise RuntimeError

DATA_DIR = Path(BASE_DIR, "data", USERNAME)
