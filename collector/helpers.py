import contextlib
import logging
import time
from pathlib import Path

logger = logging.getLogger(__name__)


@contextlib.contextmanager
def stopwatch(message: str):
    """Context manager to print how long a block of code took."""
    t0 = time.time()
    try:
        yield
    finally:
        t1 = time.time()
        logger.info("Total elapsed time for %s: %.3f" % (message, t1 - t0))


def has_session(username: str) -> bool:
    return Path(f"{username}.session").exists()
