#!/usr/bin/env python
import sqlalchemy

import settings
from personal.client import get_client
from personal.db import database, metadata
from personal.helpers import has_session
from personal.services import collect_dialogs, collect_saved_messages


def init_db():
    engine = sqlalchemy.create_engine(str(database.url))
    metadata.create_all(engine)


def main():
    init_db()
    client = get_client()
    if not has_session(settings.USERNAME):
        client.start()
    with client:
        client.loop.run_until_complete(collect_saved_messages(limit=10, iterations=1))
        client.loop.run_until_complete(collect_dialogs(limit=10))


if __name__ == "__main__":
    main()
