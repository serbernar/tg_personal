from asyncio.coroutines import iscoroutinefunction
from typing import List, Optional, Type, Union

from telethon.tl.custom.dialog import Dialog
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.tl.functions.users import GetFullUserRequest

from .client import get_client
from .helpers import async_stopwatch
from .models import Channel, Group, User


async def get_dialogs(
    archived: Optional[bool] = None,
    folder: Optional[int] = None,
    limit: Optional[float] = None,
    client=None,
) -> List[Dialog]:
    if client is None:
        client = get_client()
    async with async_stopwatch("download"):
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


class DialogResource:
    def __init__(
        self, name: str, condition, callback, model: Union[Type[User], Type[Group], Type[Channel]]
    ):
        self.name = name
        self.bucket: List[Union[User, Group, Channel]] = []
        self.condition = condition
        self.callback = callback
        self.is_coroutine = iscoroutinefunction(callback)
        self.model = model
