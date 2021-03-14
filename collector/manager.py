import csv
import logging
from asyncio import iscoroutinefunction
from pathlib import Path
from typing import List, Tuple, Union

from telethon.tl.custom.dialog import Dialog

import settings
from .models import TgChannel, TgGroup, TgUser
from .resources import get_dialogs

logger = logging.getLogger(__name__)


class DialogType:
    def __init__(self, type_name: str, datacls, condition, callback, header):
        self.name = type_name
        self.bucket: List[Union[TgUser, TgGroup, TgChannel]] = []
        self.datacls = datacls
        self.condition = condition
        self.callback = callback
        self.is_coroutine = iscoroutinefunction(callback)
        self.header = header

    def get_header(self):
        return self.header

    async def collect(self, dialog: Dialog):
        if self.is_coroutine:
            result = await self.callback(dialog)
        else:
            result = self.callback(dialog)
        self.bucket.append(result)


class DialogTypeManager:
    def __init__(self, limit=None):
        self._dialog_types = {}
        self._dialog_types_conditions = {}
        self.limit = limit

    def register_type(self, dialog_type: DialogType):
        self._dialog_types[dialog_type.name] = dialog_type
        self._dialog_types_conditions[dialog_type.name] = dialog_type.condition

    def get_dialog_type(self, dialog):
        for name, condition in self._dialog_types_conditions.items():
            if condition(dialog):
                return self._dialog_types[name]

    async def collect(self):
        logger.info("Get dialogs")
        dialogs: List[Dialog] = await get_dialogs(limit=self.limit)
        dialogs_count = len(dialogs)
        logger.info(f"Start processing {dialogs_count} dialogs")
        for dialog in dialogs:
            dialog_type = self.get_dialog_type(dialog)
            if not dialog_type:
                continue
            await dialog_type.collect(dialog=dialog)

    @staticmethod
    def _normalize(attr) -> Tuple[str, str]:
        if isinstance(attr, str):
            return attr, attr
        if len(attr) == 1:
            return attr[0], attr[0]
        return attr

    def store(self):
        settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
        for dialog_type in self._dialog_types.values():
            if not dialog_type.bucket:
                continue

            name = dialog_type.name
            normalized_header_attributes_map: List[Tuple[str, str]] = [
                self._normalize(header_attribute) for header_attribute in dialog_type.get_header()
            ]
            header = [i[0] for i in normalized_header_attributes_map]
            attributes = [i[1] for i in normalized_header_attributes_map]

            filename = f"{dialog_type.name}.csv"
            path = Path(settings.DATA_DIR, filename)

            with open(Path(settings.DATA_DIR, filename), "w") as f:
                writer = csv.writer(f)
                writer.writerow(header)
                for item in dialog_type.bucket:
                    row = [getattr(item, attribute, "") for attribute in attributes]
                    writer.writerow(row)
            logger.info(f"{name.title()} saved to {path}")
