import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from telethon.tl.custom.dialog import Dialog

from .helpers import asdict, stopwatch
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
        with stopwatch("collecting dialogs to buckets"):
            for dialog in dialogs:
                if not dialog.id:
                    continue
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
            with stopwatch(f"update rows in db={resource.model.Meta.tablename}"):
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
