import settings
from collector.client import get_client
from collector.helpers import has_session
from collector.services import collect_dialogs


def main():
    client = get_client()
    if not has_session(settings.USERNAME):
        client.start()
    with client:
        client.loop.run_until_complete(collect_dialogs())


if __name__ == "__main__":
    main()
