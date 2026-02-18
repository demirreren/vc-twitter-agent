from datetime import datetime, timezone

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from slack_sdk import WebClient

from config import GP_SLACK_USER_ID, SLACK_BOT_TOKEN, TIMEZONE
from prompts import get_next_prompt

client = WebClient(token=SLACK_BOT_TOKEN)


def _log(msg: str) -> None:
    print(f"[{datetime.now(timezone.utc).isoformat()}] [scheduler] {msg}")


def _send_prompt() -> None:
    prompt = get_next_prompt()
    _log(f"Sending prompt to GP: {prompt[:60]}…")

    try:
        dm = client.conversations_open(users=[GP_SLACK_USER_ID])
        channel_id = dm["channel"]["id"]

        client.chat_postMessage(
            channel=channel_id,
            text=(
                f"Hey! 👋 Here's your content prompt for today:\n\n"
                f"_{prompt}_\n\n"
                f"Reply with a voice memo and I'll handle the rest. 🎙️"
            ),
        )
        _log("Prompt delivered")

    except Exception as exc:
        _log(f"ERROR sending prompt: {exc}")


def start_scheduler() -> BackgroundScheduler:
    scheduler = BackgroundScheduler()
    trigger = CronTrigger(
        day_of_week="mon,wed,fri",
        hour=9,
        minute=0,
        timezone=TIMEZONE,
    )
    scheduler.add_job(_send_prompt, trigger, id="prompt_job", replace_existing=True)
    scheduler.start()
    _log(f"Scheduler started — next run: {scheduler.get_job('prompt_job').next_run_time}")
    return scheduler
