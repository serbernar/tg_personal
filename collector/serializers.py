from telethon.tl.custom.dialog import Dialog

from .client import get_client
from .models import Channel, Group, User
from .resources import get_channel_full_request, get_last_message_in_dialog, get_user_full_request


def get_group_from_dialog(dialog: Dialog) -> Group:
    return Group(
        dialog_id=dialog.id,
        title=dialog.title,
        participants_count=dialog.entity.participants_count,
        is_archived=bool(dialog.archived),
        creator=dialog.entity.creator,
    )


async def get_user_from_dialog(dialog: Dialog) -> User:
    client = get_client()
    full = await get_user_full_request(dialog=dialog, client=client)
    last_message = await get_last_message_in_dialog(dialog_id=dialog.id, client=client)
    return User(
        dialog_id=dialog.id,
        first_name=dialog.entity.first_name,
        last_name=dialog.entity.last_name,
        username=dialog.entity.username,
        bio=full.about,
        is_bot=bool(dialog.entity.bot),
        is_contact=bool(dialog.entity.contact),
        is_archived=bool(dialog.archived),
        last_message=last_message,
    )


async def get_channel_from_dialog(dialog: Dialog) -> Channel:
    full = await get_channel_full_request(channel=dialog.title)
    return Channel(
        dialog_id=dialog.id,
        title=dialog.title,
        username=dialog.entity.username,
        is_archived=bool(dialog.archived),
        about=full.full_chat.about,
    )
