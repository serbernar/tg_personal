import contextlib
import logging
import time
from pathlib import Path

from ormar import ExcludableItems

import settings

if settings.TYPE_CHECKING:  # pragma no cover
    from ormar import Model

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


def asdict(model: "Model", exclude=None):
    if exclude is None:
        exclude = []
    excludable = ExcludableItems()
    model_cls = model.__class__
    excludable.build(exclude, model_cls=model_cls, is_exclude=True)
    columns = model.own_table_columns(model_cls, excludable=excludable)
    if "id" in exclude:
        columns.remove("id")
    return {column: getattr(model, column) for column in columns}
