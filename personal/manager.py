import logging
from datetime import datetime
from typing import Dict, List, Optional

from telethon.tl.custom.dialog import Dialog

from .helpers import asdict, async_stopwatch
from .resources import DialogResource, get_dialogs

logger = logging.getLogger(__name__)


class DialogResourceManager:
    def __init__(self, limit=None):
        self._dialog_type_resources: Dict[str, DialogResource] = {}
        self.limit = limit
        self._counter = 0

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
        async with async_stopwatch("collecting dialogs to buckets"):
            for dialog in dialogs:
                if not dialog.id:
                    self._counter += 1
                    continue
                resource = self.get_dialog_resource(dialog)
                if not resource:
                    self._counter += 1
                    continue
                if resource.is_coroutine:
                    result = await resource.callback(dialog)
                else:
                    result = resource.callback(dialog)
                resource.bucket.append(result)
                self._counter += 1
                logger.info("Processed %s/%s dialogs", self._counter, dialogs_count)

    async def store(self):
        for resource in self._dialog_type_resources.values():
            async with async_stopwatch(f"update rows in db={resource.model.Meta.tablename}"):
                for item in resource.bucket:
                    query = resource.model.objects.filter(dialog_id=item.dialog_id)
                    pk = None
                    created_at = datetime.now()
                    if await query.exists():
                        result = await query.get(dialog_id=item.dialog_id)
                        pk = result.pk
                        created_at = result.created_at
                    await resource.model.objects.update_or_create(
                        pk=pk, created_at=created_at, **asdict(item, exclude=["id", "created_at"])
                    )
