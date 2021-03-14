import ormar

from .db import database, metadata


class BaseMeta(ormar.ModelMeta):
    metadata = metadata
    database = database


class Channel(ormar.Model):
    class Meta(BaseMeta):
        tablename = "channels"

    id = ormar.Integer(primary_key=True)
    dialog_id = ormar.BigInteger(nullable=True)
    archived = ormar.Boolean(default=False)

    title = ormar.String(max_length=255)
    username = ormar.String(max_length=255, nullable=True)
    about = ormar.Text(nullable=True)


class Group(ormar.Model):
    class Meta(BaseMeta):
        tablename = "groups"

    id = ormar.Integer(primary_key=True)
    dialog_id = ormar.Integer()
    archived = ormar.Boolean(default=False)

    participants_count = ormar.Integer()
    title = ormar.String(max_length=255)
    creator = ormar.Boolean(default=False)


class User(ormar.Model):
    class Meta(BaseMeta):
        tablename = "users"

    id = ormar.Integer(primary_key=True)
    dialog_id = ormar.Integer()
    archived = ormar.Boolean(default=False)

    first_name = ormar.String(max_length=255, nullable=True)
    last_name = ormar.String(max_length=255, nullable=True)
    username = ormar.String(max_length=255, nullable=True)
    bio = ormar.Text(nullable=True)
    is_bot = ormar.Boolean(default=False)
    contact = ormar.Boolean(default=False)
    last_message = ormar.Text(nullable=True)
