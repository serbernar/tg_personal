import asyncio
import logging
import time
from contextlib import asynccontextmanager, contextmanager
from pathlib import Path

from ormar import ExcludableItems
from telethon.tl.patched import Message

import settings
from .client import get_client

if settings.TYPE_CHECKING:  # pragma no cover
    from ormar import Model

logger = logging.getLogger(__name__)


class MessageContainer:
    def __init__(self, text):
        self.text = text

    def get(self):
        return self.text

    def set(self, value):
        self.text = value


@contextmanager
def stopwatch(message: str):
    """Context manager to print how long a block of code took."""
    t0 = time.time()
    container = MessageContainer(message)
    try:
        yield container
    finally:
        t1 = time.time()
        logger.info("Total elapsed time for %s: %.3f" % (container.get(), t1 - t0))


@asynccontextmanager
async def async_stopwatch(message: str):
    t0 = time.time()
    container = MessageContainer(message)
    try:
        yield container
    finally:
        t1 = time.time()
        logger.info("Total elapsed time for %s: %.3f" % (container.get(), t1 - t0))


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


def progress_callback(current, total):
    logger.info("Downloaded %d out of %d bytes: %.2f", current, total, current / total)


async def download_media(message: Message):
    client = get_client()
    if message.media is not None and message.file:
        name = message.file.name or message.file.id
        file_path = f"{settings.DATA_DIR}/{name}{message.file.ext}"
        await client.download_media(
            message=message, file=file_path, progress_callback=progress_callback
        )


async def download_message(message: Message):
    await asyncio.sleep(0)
    logger.info(message.text)
