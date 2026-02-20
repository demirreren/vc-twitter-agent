from datetime import datetime, timezone

from flask import Blueprint, request
from slack_sdk import WebClient
from twilio.twiml.messaging_response import MessagingResponse

from config import GP_WHATSAPP_NUMBER, SLACK_BOT_TOKEN, TWITTER_CHANNEL_ID
from prompts import get_last_prompt

webhook_bp = Blueprint("webhook", __name__)
slack_client = WebClient(token=SLACK_BOT_TOKEN)


def _log(msg: str) -> None:
    print(f"[{datetime.now(timezone.utc).isoformat()}] [webhook] {msg}")


@webhook_bp.route("/webhook", methods=["POST"])
def whatsapp_webhook():
    sender = request.form.get("From", "")
    body = request.form.get("Body", "").strip()

    if sender != GP_WHATSAPP_NUMBER:
        _log(f"Ignoring message from unknown sender: {sender}")
        return str(MessagingResponse()), 200

    if not body:
        _log("Received empty message from GP — ignoring")
        return str(MessagingResponse()), 200

    _log(f"Received WhatsApp reply from GP ({len(body)} chars)")

    prompt = get_last_prompt()
    date_str = datetime.now(timezone.utc).strftime("%B %d, %Y")

    try:
        slack_client.chat_postMessage(
            channel=TWITTER_CHANNEL_ID,
            text=(
                f"*New content from GP — {date_str}*\n\n"
                f"*Prompt:* {prompt}\n\n"
                f"*Response:*\n{body}"
            ),
        )
        _log("Posted GP response to #twitter channel")

    except Exception as exc:
        _log(f"ERROR posting to #twitter: {exc}")

    twiml = MessagingResponse()
    return str(twiml), 200
