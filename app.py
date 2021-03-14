import sqlalchemy

import settings
from collector.client import get_client
from collector.db import database, metadata
from collector.helpers import has_session
from collector.services import collect_dialogs


def init_db():
    engine = sqlalchemy.create_engine(str(database.url))
    metadata.create_all(engine)


def main():
    init_db()
    client = get_client()
    if not has_session(settings.USERNAME):
        client.start()
    with client:
        client.loop.run_until_complete(collect_dialogs())


if __name__ == "__main__":
    main()
