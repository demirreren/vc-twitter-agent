"""
Downloads a Slack-hosted voice memo file and transcribes it with
OpenAI's Whisper API.  Returns the transcript text.
"""

import tempfile
from datetime import datetime, timezone

import requests
from openai import OpenAI

from config import OPENAI_API_KEY, SLACK_BOT_TOKEN


openai_client = OpenAI(api_key=OPENAI_API_KEY)


def _log(msg: str) -> None:
    print(f"[{datetime.now(timezone.utc).isoformat()}] [transcribe] {msg}")


def download_and_transcribe(file_url: str) -> str:
    """
    Download a voice memo from Slack's servers and send it to
    OpenAI Whisper for transcription.

    Parameters
    ----------
    file_url : str
        The ``url_private_download`` value from the Slack file object.

    Returns
    -------
    str
        The transcribed text.

    Raises
    ------
    RuntimeError
        If the download or transcription fails.
    """
    _log(f"Downloading voice memo from {file_url}")

    headers = {"Authorization": f"Bearer {SLACK_BOT_TOKEN}"}
    resp = requests.get(file_url, headers=headers, timeout=60)

    if resp.status_code != 200:
        raise RuntimeError(
            f"Failed to download voice memo (HTTP {resp.status_code})"
        )

    # Whisper needs a real file with an extension so it can detect the codec.
    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
        tmp.write(resp.content)
        tmp_path = tmp.name

    _log(f"Transcribing {tmp_path} ({len(resp.content)} bytes)")

    with open(tmp_path, "rb") as audio_file:
        transcription = openai_client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
        )

    text = transcription.text.strip()
    _log(f"Transcription complete ({len(text)} chars)")
    return text
