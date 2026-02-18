from datetime import datetime, timezone

from slack_bolt.adapter.socket_mode import SocketModeHandler

from bot import app
from config import SLACK_APP_TOKEN
from scheduler import start_scheduler


def _log(msg: str) -> None:
    print(f"[{datetime.now(timezone.utc).isoformat()}] [main] {msg}")


if __name__ == "__main__":
    _log("Starting Northside Ventures Slack Bot…")
    start_scheduler()
    _log("Connecting to Slack via Socket Mode…")
    SocketModeHandler(app, SLACK_APP_TOKEN).start()
