import logging
from typing import Dict, List, Optional

from telethon.tl.custom.dialog import Dialog

from .helpers import asdict, async_stopwatch
from .resources import DialogResource, get_dialogs

logger = logging.getLogger(__name__)


class DialogResourceManager:
    def __init__(self, limit=None):
        self._dialog_type_resources: Dict[str, DialogResource] = {}
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
        async with async_stopwatch("processing dialogs"):
            for dialog in dialogs:
                if not dialog.id:
                    continue
                resource = self.get_dialog_resource(dialog)
                if not resource:
                    continue
                result = await resource.callback(dialog)
                await self.store(resource, result)

    @staticmethod
    async def store(resource, item):
        model = resource.model
        async with async_stopwatch(f"%s row in {model.Meta.tablename}") as message:
            query = model.objects.filter(dialog_id=item.dialog_id)
            pk = None
            text = message.get()
            if await query.exists():
                result = await query.get(dialog_id=item.dialog_id)
                pk = result.pk
                message.set(text % "update")
            else:
                message.set(text % "create")
            await model.objects.update_or_create(
                pk=pk, **asdict(item, exclude=["id", "created_at"])
            )
