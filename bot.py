from datetime import datetime, timezone

from slack_bolt import App
from slack_sdk import WebClient

from canvas_logger import append_entry
from config import GP_SLACK_USER_ID, SLACK_BOT_TOKEN, TWITTER_CHANNEL_ID
from prompts import PROMPTS, _load_index
from transcribe import download_and_transcribe

app = App(token=SLACK_BOT_TOKEN)


def _log(msg: str) -> None:
    print(f"[{datetime.now(timezone.utc).isoformat()}] [bot] {msg}")


def _is_voice_memo(file_obj: dict) -> bool:
    mime = file_obj.get("mimetype", "")
    subtype = file_obj.get("subtype", "")
    filetype = file_obj.get("filetype", "")
    return (
        mime.startswith("audio/")
        or subtype == "slack_audio"
        or filetype in ("webm", "mp4", "m4a", "ogg", "mp3")
    )


@app.event("message")
def handle_message(event: dict, client: WebClient) -> None:
    if event.get("channel_type") != "im":
        return
    if event.get("user") != GP_SLACK_USER_ID:
        return
    if event.get("subtype") not in (None, "file_share"):
        return

    files = event.get("files", [])
    voice_files = [f for f in files if _is_voice_memo(f)]

    if not voice_files:
        return

    dm_channel = event["channel"]

    # The scheduler already advanced the index after sending, so the
    # most recently sent prompt is one behind the current pointer.
    idx = (_load_index() - 1) % len(PROMPTS)
    prompt = PROMPTS[idx]

    for vf in voice_files:
        file_url = vf.get("url_private_download")
        if not file_url:
            _log("Voice memo has no download URL — skipping")
            continue

        _log(f"Processing voice memo {vf.get('id')}")

        try:
            transcript = download_and_transcribe(file_url)
        except Exception as exc:
            _log(f"ERROR transcribing: {exc}")
            client.chat_postMessage(
                channel=dm_channel,
                text=(
                    "⚠️ I couldn't transcribe that voice memo. "
                    "Could you try re-recording and sending it again?"
                ),
            )
            client.chat_postMessage(
                channel=TWITTER_CHANNEL_ID,
                text=f"⚠️ Voice memo transcription failed: {exc}",
            )
            continue

        date_str = datetime.now(timezone.utc).strftime("%B %d, %Y")

        try:
            client.chat_postMessage(
                channel=TWITTER_CHANNEL_ID,
                text=(
                    f"🎙️ *New content idea — {date_str}*\n\n"
                    f"*Prompt:* {prompt}\n\n"
                    f"*Transcript:*\n{transcript}\n\n"
                    f"✅ Logged to the channel canvas."
                ),
            )
        except Exception as exc:
            _log(f"ERROR posting to #twitter: {exc}")

        append_entry(client, prompt, transcript, date_str)

        try:
            client.chat_postMessage(
                channel=dm_channel,
                text="✅ Got it! Your voice memo has been transcribed and posted to #twitter.",
            )
        except Exception as exc:
            _log(f"ERROR confirming to GP: {exc}")
