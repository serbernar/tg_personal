from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Union


@dataclass
class TgBase:
    id: Union[str, int]
    archived: bool


@dataclass
class TgChannel(TgBase):
    title: str
    username: Optional[str]
    about: Optional[str]


@dataclass
class TgGroup(TgBase):
    title: str
    participants_count: int
    date: datetime
    creator: bool


@dataclass
class TgUser(TgBase):
    first_name: str
    last_name: Optional[str]
    username: Optional[str]
    bio: Optional[str]
    is_bot: bool
    contact: bool
    last_message: Optional[str]
