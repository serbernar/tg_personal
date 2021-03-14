import logging
from asyncio import iscoroutinefunction
from typing import List, Optional, Tuple, Union

from telethon.tl.custom.dialog import Dialog

from .helpers import stopwatch
from .models import Channel, Group, User
from .resources import get_dialogs

logger = logging.getLogger(__name__)


class DialogResource:
    def __init__(self, name: str, condition, callback, model: Union[User, Group, Channel]):
        self.name = name
        self.bucket: List[Union[User, Group, Channel]] = []
        self.condition = condition
        self.callback = callback
        self.is_coroutine = iscoroutinefunction(callback)
        self.model = model


class DialogResourceManager:
    def __init__(self, limit=None):
        self._dialog_type_resources = {}
        self.limit = limit

    def register_resource(self, resource: DialogResource):
        self._dialog_type_resources[resource.name] = resource

    def get_dialog_resource(self, dialog) -> Optional[DialogResource]:
        for resource in self._dialog_type_resources.values():
            if resource.condition(dialog):
                return resource

    async def collect(self):
        logger.info("Get dialogs")
        dialogs: List[Dialog] = await get_dialogs(limit=self.limit)
        dialogs_count = len(dialogs)
        logger.info(f"Start processing {dialogs_count} dialogs")
        with stopwatch("collecting dialogs to buckets"):
            for dialog in dialogs:
                resource = self.get_dialog_resource(dialog)
                if not resource:
                    continue
                if resource.is_coroutine:
                    result = await resource.callback(dialog)
                else:
                    result = resource.callback(dialog)
                resource.bucket.append(result)

    @staticmethod
    def _normalize(attr) -> Tuple[str, str]:
        if isinstance(attr, str):
            return attr, attr
        if len(attr) == 1:
            return attr[0], attr[0]
        return attr

    async def store(self):
        for resource in self._dialog_type_resources.values():
            with stopwatch(f"bulk create in db={resource.model.Meta.tablename}"):
                items = [item for item in resource.bucket]
                await resource.model.objects.bulk_create(items)
