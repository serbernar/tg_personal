import csv
from dataclasses import dataclass
from datetime import datetime
from os import getenv
from typing import List, Optional

from dotenv import load_dotenv
from telethon.sync import TelegramClient
from telethon.tl.custom.dialog import Dialog
from telethon.tl.functions.channels import GetFullChannelRequest


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


def get_group_from_dialog(dialog):
    return TgGroup(
        title=dialog.title,
        participants_count=dialog.entity.participants_count,
        archived=dialog.archived,
        date=dialog.entity.date,
        creator=dialog.entity.creator,
    )


async def get_channel_from_dialog(dialog, tg_client):
    channel_full = await tg_client(GetFullChannelRequest(channel=dialog.title))
    about = channel_full.full_chat.about
    return TgChannel(
        title=dialog.title,
        username=dialog.entity.username,
        archived=dialog.archived,
        about=about,
    )


async def get_dialogs(
    tg_client: TelegramClient,
    archived: Optional[bool] = None,
    folder: Optional[int] = None,
    limit: Optional[float] = None,
):
    dialogs: List[Dialog] = await tg_client.get_dialogs(
        ignore_pinned=True, archived=archived, folder=folder, limit=limit
    )
    return dialogs


async def collect(tg_client):
    print("get dialogs")
    dialogs: List[Dialog] = await get_dialogs(tg_client=tg_client)
    groups = []
    channels = []
    print(f"processing {len(dialogs)} dialogs")
    for idx, dialog in enumerate(dialogs, start=1):
        print(f"processing {idx} dialog")
        if dialog.is_channel:
            channel = await get_channel_from_dialog(dialog, tg_client=tg_client)
            channels.append(channel)
        elif dialog.is_group:
            groups.append(get_group_from_dialog(dialog))

    print(f"Collected {len(groups)} groups")
    with open("groups.csv", "w") as f:
        writer = csv.writer(f)
        writer.writerow(["title", "participants_count", "creator", "archived"])
        for group in groups:
            writer.writerow(
                [group.title, group.participants_count, group.creator, group.archived]
            )

    print(f"Collected {len(channels)} channels")
    with open("channels.csv", "w") as f:
        writer = csv.writer(f)
        writer.writerow(["title", "username", "archived", "about"])
        for channel in channels:
            writer.writerow(
                [channel.title, channel.username, channel.archived, channel.about]
            )


def main():
    load_dotenv(".env")
    api_id = int(getenv("API_ID"))
    api_hash = getenv("API_HASH")
    username = getenv("USERNAME")

    client = TelegramClient(username, api_id, api_hash)
    with client:
        client.loop.run_until_complete(collect(tg_client=client))


if __name__ == "__main__":
    main()
