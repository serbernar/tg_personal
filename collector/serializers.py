from telethon.tl.custom.dialog import Dialog

from .client import get_client
from .models import TgChannel, TgGroup, TgUser
from .resources import get_channel_full_request, get_last_message_in_dialog, get_user_full_request


def get_group_from_dialog(dialog: Dialog) -> TgGroup:
    return TgGroup(
        id=dialog.id,
        title=dialog.title,
        participants_count=dialog.entity.participants_count,
        archived=dialog.archived,
        date=dialog.entity.date,
        creator=dialog.entity.creator,
    )


async def get_user_from_dialog(dialog: Dialog) -> TgUser:
    client = get_client()
    full = await get_user_full_request(dialog=dialog, client=client)
    last_message = await get_last_message_in_dialog(dialog_id=dialog.id, client=client)
    return TgUser(
        id=dialog.id,
        first_name=dialog.entity.first_name,
        last_name=dialog.entity.last_name,
        username=dialog.entity.username,
        bio=full.about,
        is_bot=dialog.entity.bot,
        contact=dialog.entity.contact,
        archived=dialog.archived,
        last_message=last_message,
    )


async def get_channel_from_dialog(dialog: Dialog) -> TgChannel:
    full = await get_channel_full_request(channel=dialog.title)
    return TgChannel(
        id=dialog.id,
        title=dialog.title,
        username=dialog.entity.username,
        archived=dialog.archived,
        about=full.full_chat.about,
    )
