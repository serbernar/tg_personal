import ormar

from .db import database, metadata


class BaseMeta(ormar.ModelMeta):
    metadata = metadata
    database = database


class Channel(ormar.Model):
    class Meta(BaseMeta):
        tablename = "channels"

    id = ormar.Integer(primary_key=True)
    dialog_id = ormar.BigInteger()
    is_archived = ormar.Boolean(default=False)

    title = ormar.String(max_length=255)
    username = ormar.String(max_length=255, nullable=True)
    about = ormar.Text(nullable=True)

    def as_dict(self):
        return {
            "dialog_id": self.dialog_id,
            "is_archived": self.is_archived,
            "title": self.title,
            "username": self.username,
            "about": self.about,
        }


class Group(ormar.Model):
    class Meta(BaseMeta):
        tablename = "groups"

    id = ormar.Integer(primary_key=True)
    dialog_id = ormar.Integer()
    is_archived = ormar.Boolean(default=False)

    participants_count = ormar.Integer()
    title = ormar.String(max_length=255)
    creator = ormar.Boolean(default=False)

    def as_dict(self):
        return {
            "dialog_id": self.dialog_id,
            "is_archived": self.is_archived,
            "title": self.title,
            "participants_count": self.participants_count,
            "creator": self.creator,
        }


class User(ormar.Model):
    class Meta(BaseMeta):
        tablename = "users"

    id = ormar.Integer(primary_key=True)
    dialog_id = ormar.Integer()
    is_archived = ormar.Boolean(default=False)

    first_name = ormar.String(max_length=255, nullable=True)
    last_name = ormar.String(max_length=255, nullable=True)
    username = ormar.String(max_length=255, nullable=True)
    bio = ormar.Text(nullable=True)
    is_bot = ormar.Boolean(default=False)
    is_contact = ormar.Boolean(default=False)
    last_message = ormar.Text(nullable=True)

    def as_dict(self):
        return {
            "dialog_id": self.dialog_id,
            "is_archived": self.is_archived,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "username": self.username,
            "bio": self.bio,
            "is_bot": self.is_bot,
            "is_contact": self.is_contact,
            "last_message": self.last_message,
        }
