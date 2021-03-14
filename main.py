import contextlib
import csv
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple, Union

from telethon.sync import TelegramClient
from telethon.tl.custom.dialog import Dialog
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.tl.functions.users import GetFullUserRequest

import settings


@contextlib.contextmanager
def stopwatch(message: str):
    """Context manager to print how long a block of code took."""
    t0 = time.time()
    try:
        yield
    finally:
        t1 = time.time()
        print("Total elapsed time for %s: %.3f" % (message, t1 - t0))


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


@dataclass
class TgUser:
    first_name: str
    last_name: Optional[str]
    username: Optional[str]
    bio: Optional[str]
    is_bot: bool
    contact: bool
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


def get_group_from_dialog(dialog: Dialog) -> TgGroup:
    return TgGroup(
        title=dialog.title,
        participants_count=dialog.entity.participants_count,
        archived=dialog.archived,
        date=dialog.entity.date,
        creator=dialog.entity.creator,
    )


async def get_user_from_dialog(dialog: Dialog) -> TgUser:
    client = get_client()
    full = await client(GetFullUserRequest(dialog))
    return TgUser(
        first_name=dialog.entity.first_name,
        last_name=dialog.entity.last_name,
        username=dialog.entity.username,
        bio=full.about,
        is_bot=dialog.entity.bot,
        contact=dialog.entity.contact,
        archived=dialog.archived,
    )


async def get_channel_from_dialog(dialog: Dialog) -> TgChannel:
    client = get_client()
    full = await client(GetFullChannelRequest(channel=dialog.title))
    return TgChannel(
        title=dialog.title,
        username=dialog.entity.username,
        archived=dialog.archived,
        about=full.full_chat.about,
    )


async def get_dialogs(
    archived: Optional[bool] = None,
    folder: Optional[int] = None,
    limit: Optional[float] = None,
) -> List[Dialog]:
    client = get_client()
    with stopwatch("download"):
        dialogs: List[Dialog] = await client.get_dialogs(
            ignore_pinned=True, archived=archived, folder=folder, limit=limit
        )
        return dialogs


def store_data(
    objects: Union[List[TgUser], List[TgGroup], List[TgChannel]],
    filename: str,
    header_attributes_map: List[Union[str, Tuple[str], Tuple[str, str]]],
):
    if not objects:
        return

    name = filename

    def normalize(attr) -> Tuple[str, str]:
        if isinstance(attr, str):
            return attr, attr
        if len(attr) == 1:
            return attr[0], attr[0]
        return attr

    normalized_header_attributes_map: List[Tuple[str, str]] = [
        normalize(header_attribute) for header_attribute in header_attributes_map
    ]
    header = [i[0] for i in normalized_header_attributes_map]
    attributes = [i[1] for i in normalized_header_attributes_map]

    filename = f"{filename}.csv"
    path = Path(settings.DATA_DIR, filename)

    with open(Path(settings.DATA_DIR, filename), "w") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        for obj in objects:
            row = [getattr(obj, attribute, "") for attribute in attributes]
            writer.writerow(row)
    print(f"{name.title()} saved to {path}")


def save_users(users: Optional[List[TgUser]]):
    if not users:
        return
    print(f"Collected {len(users)} users")
    with open(Path(settings.DATA_DIR, "users.csv"), "w") as f:
        writer = csv.writer(f)
        writer.writerow(
            ["first_name", "last_name", "username", "bio", "is_bot", "contact", "archived"]
        )
        for user in users:
            writer.writerow(
                [
                    user.first_name,
                    user.last_name,
                    user.username,
                    user.bio,
                    user.is_bot,
                    user.contact,
                    user.archived,
                ]
            )


def save_channels(channels: Optional[List[TgChannel]]):
    if not channels:
        return
    print(f"Save {len(channels)} channels")
    with open(Path(settings.DATA_DIR, "channels.csv"), "w") as f:
        writer = csv.writer(f)
        writer.writerow(["title", "username", "archived", "about"])
        for channel in channels:
            writer.writerow([channel.title, channel.username, channel.archived, channel.about])


async def collect():
    print("Get dialogs")
    dialogs: List[Dialog] = await get_dialogs()
    groups = []
    channels = []
    users = []
    dialogs_count = len(dialogs)
    print(f"Start processing {dialogs_count} dialogs")
    with stopwatch("extract dialogs"):
        counter = 0
        for dialog in dialogs:
            if dialog.is_channel:
                channel = await get_channel_from_dialog(dialog)
                channels.append(channel)
            elif dialog.is_group:
                groups.append(get_group_from_dialog(dialog))
            elif dialog.is_user and not dialog.entity.support:
                user = await get_user_from_dialog(dialog)
                users.append(user)
            counter += 1
            if counter % 10 == 0:
                print(f"Processed {counter}/{dialogs_count} dialogs")

    settings.DATA_DIR.mkdir(parents=True, exist_ok=True)

    store_data(
        groups, "groups", ["title", ("members", "participants_count"), "creator", "archived"]
    )
    store_data(
        users,
        "users",
        ["first_name", "last_name", "username", "bio", "is_bot", "contact", "archived"],
    )
    store_data(channels, "channels", ["title", "username", "archived", "about"])


def has_session(username: str) -> bool:
    return Path(f"{username}.session").exists()


def main():
    client = get_client()
    if not has_session(settings.USERNAME):
        client.start()
    with client:
        client.loop.run_until_complete(collect())


if __name__ == "__main__":
    main()
