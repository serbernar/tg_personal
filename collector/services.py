import logging

from .manager import DialogResourceManager
from .models import Channel, Group, User
from .resources import DialogResource
from .serializers import get_channel_from_dialog, get_group_from_dialog, get_user_from_dialog

logger = logging.getLogger(__name__)


async def collect_dialogs(limit=None):
    channels_dialogs = DialogResource(
        name="channels",
        condition=lambda d: d.is_channel,
        callback=get_channel_from_dialog,
        model=Channel,
    )
    groups_dialogs = DialogResource(
        name="groups",
        model=Group,
        condition=lambda d: d.is_group,
        callback=get_group_from_dialog,
    )
    users_dialogs = DialogResource(
        name="users",
        condition=lambda d: d.is_user and not d.entity.support,
        callback=get_user_from_dialog,
        model=User,
    )
    manager = DialogResourceManager(limit=limit)
    manager.register_resource(channels_dialogs)
    manager.register_resource(groups_dialogs)
    manager.register_resource(users_dialogs)
    await manager.collect()
    await manager.store()
