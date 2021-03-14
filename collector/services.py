import logging

from .manager import DialogType, DialogTypeManager
from .models import TgChannel, TgGroup, TgUser
from .serializers import get_channel_from_dialog, get_group_from_dialog, get_user_from_dialog

logger = logging.getLogger(__name__)


async def collect_dialogs():
    channels_dialogs = DialogType(
        type_name="channels",
        datacls=TgChannel,
        condition=lambda d: d.is_channel,
        callback=get_channel_from_dialog,
        header=["id", "title", "username", "archived", "about"],
    )
    groups_dialogs = DialogType(
        type_name="groups",
        datacls=TgGroup,
        condition=lambda d: d.is_group,
        callback=get_group_from_dialog,
        header=["id", "title", ("members", "participants_count"), "creator", "archived"],
    )
    users_dialogs = DialogType(
        type_name="users",
        datacls=TgUser,
        condition=lambda d: d.is_user and not d.entity.support,
        callback=get_user_from_dialog,
        header=[
            "id",
            "username",
            "first_name",
            "last_name",
            "bio",
            "is_bot",
            "contact",
            "archived",
            "last_message",
        ],
    )
    manager = DialogTypeManager(limit=30)
    manager.register_type(channels_dialogs)
    manager.register_type(groups_dialogs)
    manager.register_type(users_dialogs)
    await manager.collect()

    manager.store()
