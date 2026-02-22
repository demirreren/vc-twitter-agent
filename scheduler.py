from datetime import datetime, timezone

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from twilio.rest import Client

from config import (
    GP_WHATSAPP_NUMBER,
    TIMEZONE,
    TWILIO_ACCOUNT_SID,
    TWILIO_AUTH_TOKEN,
    TWILIO_WHATSAPP_FROM,
)
from prompts import get_next_prompt

twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)


def _log(msg: str) -> None:
    print(f"[{datetime.now(timezone.utc).isoformat()}] [scheduler] {msg}")


def _send_prompt() -> None:
    prompt = get_next_prompt()
    _log(f"Sending prompt to GP: {prompt[:60]}…")

    try:
        twilio_client.messages.create(
            from_=TWILIO_WHATSAPP_FROM,
            to=GP_WHATSAPP_NUMBER,
            body=(
                f"Hey, it's Leif! Here's your content prompt for today:\n\n"
                f"{prompt}\n\n"
                f"Just reply with your thoughts and I'll handle the rest!"
            ),
        )
        _log("Prompt delivered via WhatsApp")

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
