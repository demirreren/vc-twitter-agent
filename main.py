import os
from datetime import datetime, timezone

from flask import Flask

from bot import webhook_bp
from scheduler import start_scheduler


def _log(msg: str) -> None:
    print(f"[{datetime.now(timezone.utc).isoformat()}] [main] {msg}")


def create_app() -> Flask:
    app = Flask(__name__)
    app.register_blueprint(webhook_bp)
    return app


if __name__ == "__main__":
    _log("Starting Northside Ventures WhatsApp Bot…")
    start_scheduler()
    app = create_app()
    port = int(os.environ.get("PORT", 8080))
    _log(f"Starting Flask server on port {port}…")
    app.run(host="0.0.0.0", port=port)
