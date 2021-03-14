import csv
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from telethon.sync import TelegramClient
from telethon.tl.custom.dialog import Dialog
from telethon.tl.functions.channels import GetFullChannelRequest

import settings


@dataclass
class TgChannel:
    title: str
    username: Optional[str]
    about: Optional[str]
    archived: bool


@dataclass
class TgGroup:
    title: str
    participants_count: int
    date: datetime
    creator: bool
    archived: bool


_client = None


def get_client() -> TelegramClient:
    global _client
    if _client is None:
        _client = TelegramClient(
            session=settings.USERNAME,
            api_id=settings.API_ID,
            api_hash=settings.API_HASH,
        )
    return _client


def get_group_from_dialog(dialog):
    return TgGroup(
        title=dialog.title,
        participants_count=dialog.entity.participants_count,
        archived=dialog.archived,
        date=dialog.entity.date,
        creator=dialog.entity.creator,
    )


async def get_channel_from_dialog(dialog):
    client = get_client()
    channel_full = await client(GetFullChannelRequest(channel=dialog.title))
    about = channel_full.full_chat.about
    return TgChannel(
        title=dialog.title,
        username=dialog.entity.username,
        archived=dialog.archived,
        about=about,
    )


async def get_dialogs(
    archived: Optional[bool] = None,
    folder: Optional[int] = None,
    limit: Optional[float] = None,
):
    client = get_client()
    dialogs: List[Dialog] = await client.get_dialogs(
        ignore_pinned=True, archived=archived, folder=folder, limit=limit
    )
    return dialogs


def save_groups(groups):
    if not groups:
        return
    print(f"Collected {len(groups)} groups")
    with open(Path(settings.DATA_DIR, "groups.csv"), "w") as f:
        writer = csv.writer(f)
        writer.writerow(["title", "participants_count", "creator", "archived"])
        for group in groups:
            writer.writerow(
                [group.title, group.participants_count, group.creator, group.archived]
            )


def save_channels(channels):
    if not channels:
        return
    print(f"Save {len(channels)} channels")
    with open(Path(settings.DATA_DIR, "channels.csv"), "w") as f:
        writer = csv.writer(f)
        writer.writerow(["title", "username", "archived", "about"])
        for channel in channels:
            writer.writerow(
                [channel.title, channel.username, channel.archived, channel.about]
            )


async def collect():
    print("get dialogs")
    dialogs: List[Dialog] = await get_dialogs()
    groups = []
    channels = []
    print(f"processing {len(dialogs)} dialogs")
    for idx, dialog in enumerate(dialogs, start=1):
        print(f"processing {idx} dialog")
        if dialog.is_channel:
            channel = await get_channel_from_dialog(dialog)
            channels.append(channel)
        elif dialog.is_group:
            groups.append(get_group_from_dialog(dialog))

    settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
    save_groups(groups)
    save_channels(channels)


def check_session():
    if not Path(f"{settings.USERNAME}.session").exists():
        client = get_client()
        client.start()


def main():
    client = get_client()
    with client:
        client.loop.run_until_complete(collect())


if __name__ == "__main__":
    check_session()
    main()
