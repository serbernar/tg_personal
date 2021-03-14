from typing import List, Optional

from telethon.tl.custom.dialog import Dialog
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.tl.functions.users import GetFullUserRequest

from .client import get_client
from .helpers import stopwatch


async def get_dialogs(
    archived: Optional[bool] = None,
    folder: Optional[int] = None,
    limit: Optional[float] = None,
    client=None,
) -> List[Dialog]:
    if client is None:
        client = get_client()
    with stopwatch("download"):
        dialogs: List[Dialog] = await client.get_dialogs(
            ignore_pinned=True, archived=archived, folder=folder, limit=limit
        )
        return dialogs


async def get_user_full_request(dialog, client=None):
    if client is None:
        client = get_client()
    full = await client(GetFullUserRequest(dialog))
    return full


async def get_last_message_in_dialog(dialog_id, client=None):
    if client is None:
        client = get_client()
    async for message in client.iter_messages(dialog_id, limit=1):
        return message.text


async def get_channel_full_request(channel, client=None):
    if client is None:
        client = get_client()
    full = await client(GetFullChannelRequest(channel=channel))
    return full
