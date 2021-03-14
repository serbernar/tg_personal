from datetime import datetime

import ormar

from .db import database, metadata


class BaseModel(ormar.Model):
    class Meta:
        abstract = True
        metadata = metadata
        database = database

    id = ormar.Integer(primary_key=True)
    dialog_id = ormar.BigInteger(unique=True)
    is_archived = ormar.Boolean(default=False)

    created_at: datetime = ormar.DateTime(default=datetime.now)
    updated_at: datetime = ormar.DateTime(default=datetime.now)


class BaseMeta(ormar.ModelMeta):
    metadata = metadata
    database = database


class Channel(BaseModel):
    class Meta(BaseMeta):
        tablename = "channels"

    title = ormar.String(max_length=255)
    username = ormar.String(max_length=255, nullable=True)
    about = ormar.Text(nullable=True)


class Group(BaseModel):
    class Meta(BaseMeta):
        tablename = "groups"

    participants_count = ormar.Integer()
    title = ormar.String(max_length=255)
    creator = ormar.Boolean(default=False)


class User(BaseModel):
    class Meta(BaseMeta):
        tablename = "users"

    first_name = ormar.String(max_length=255, nullable=True)
    last_name = ormar.String(max_length=255, nullable=True)
    username = ormar.String(max_length=255, nullable=True)
    bio = ormar.Text(nullable=True)
    is_bot = ormar.Boolean(default=False)
    is_contact = ormar.Boolean(default=False)
    last_message = ormar.Text(nullable=True)
