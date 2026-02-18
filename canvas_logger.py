"""
Manages the #twitter channel Canvas in Slack.

Flow:
  1. Check if #twitter already has a canvas via conversations.info.
  2. If not, create one with conversations.canvases.create.
  3. Append each new entry (date + prompt + transcript) via canvases.edit
     using the insert_at_end operation.
"""

from datetime import datetime, timezone

from slack_sdk import WebClient

from config import TWITTER_CHANNEL_ID


def _log(msg: str) -> None:
    print(f"[{datetime.now(timezone.utc).isoformat()}] [canvas] {msg}")


def _get_existing_canvas_id(client: WebClient) -> str | None:
    """Return the canvas file_id attached to #twitter, or None."""
    resp = client.conversations_info(channel=TWITTER_CHANNEL_ID)
    canvas_id = (
        resp["channel"]
        .get("properties", {})
        .get("canvas", {})
        .get("file_id")
    )
    if canvas_id:
        _log(f"Found existing canvas: {canvas_id}")
    return canvas_id


def _create_canvas(client: WebClient) -> str:
    """Create a new channel canvas on #twitter and return its ID."""
    _log("No canvas found — creating one now")
    resp = client.conversations_canvases_create(
        channel_id=TWITTER_CHANNEL_ID,
        document_content={
            "type": "markdown",
            "markdown": (
                "# 🐦 Northside Ventures — Content Ideas Log\n"
                "Each entry below is a transcribed voice memo from the GP.\n\n---"
            ),
        },
    )
    canvas_id = resp["canvas_id"]
    _log(f"Created canvas: {canvas_id}")
    return canvas_id


def _ensure_canvas(client: WebClient) -> str:
    """Return the canvas ID, creating the canvas if necessary."""
    return _get_existing_canvas_id(client) or _create_canvas(client)


def append_entry(
    client: WebClient,
    prompt: str,
    transcript: str,
    date_str: str | None = None,
) -> None:
    """
    Append a new prompt + transcript section to the channel canvas.

    If anything goes wrong the error is logged but never raised — the
    caller should still post the message to #twitter so the social
    media manager isn't left in the dark.
    """
    if date_str is None:
        date_str = datetime.now(timezone.utc).strftime("%B %d, %Y")

    try:
        canvas_id = _ensure_canvas(client)

        entry_markdown = (
            f"## {date_str}\n"
            f"**Prompt:** {prompt}\n\n"
            f"**Transcript:**\n{transcript}\n\n---"
        )

        client.canvases_edit(
            canvas_id=canvas_id,
            changes=[
                {
                    "operation": "insert_at_end",
                    "document_content": {
                        "type": "markdown",
                        "markdown": entry_markdown,
                    },
                }
            ],
        )
        _log("Entry appended to canvas")

    except Exception as exc:
        _log(f"ERROR writing to canvas: {exc}")
