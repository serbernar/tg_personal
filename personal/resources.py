from typing import List, Optional, Type, Union

from telethon.tl.custom.dialog import Dialog
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.tl.functions.users import GetFullUserRequest

import settings
from .client import get_client
from .helpers import async_stopwatch
from .models import Channel, Group, User

# from telethon.tl.types import InputMessagesFilterEmpty


async def get_dialogs(
    archived: Optional[bool] = None,
    folder: Optional[int] = None,
    limit: Optional[float] = None,
) -> List[Dialog]:
    client = get_client()
    async with async_stopwatch("download"):
        dialogs: List[Dialog] = await client.get_dialogs(
            ignore_pinned=True, archived=archived, folder=folder, limit=limit
        )
        return dialogs


async def get_user_full_request(dialog):
    client = get_client()
    full = await client(GetFullUserRequest(dialog))
    return full


async def get_last_message_in_dialog(dialog_id):
    client = get_client()
    async for message in client.iter_messages(dialog_id, limit=1):
        return message.text


async def get_channel_full_request(channel):
    client = get_client()
    full = await client(GetFullChannelRequest(channel=channel))
    return full


async def get_drafts():
    client = get_client()
    entity = await client.get_entity(settings.USERNAME)
    drafts = await client.get_drafts(entity)
    return drafts


class DialogResource:
    def __init__(
        self, name: str, condition, callback, model: Union[Type[User], Type[Group], Type[Channel]]
    ):
        self.name = name
        self.condition = condition
        self.callback = callback
        self.model = model
