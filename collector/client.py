from telethon.sync import TelegramClient

import settings

_client = None


def get_client() -> TelegramClient:
    global _client
    if _client is None:
        _client = TelegramClient(
            session=settings.USERNAME,
            api_id=settings.API_ID,
            api_hash=settings.API_HASH,
        )
    return _client
