import os
from dotenv import load_dotenv

load_dotenv()

SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
TWITTER_CHANNEL_ID = os.environ["TWITTER_CHANNEL_ID"]

TWILIO_ACCOUNT_SID = os.environ["TWILIO_ACCOUNT_SID"]
TWILIO_AUTH_TOKEN = os.environ["TWILIO_AUTH_TOKEN"]
TWILIO_WHATSAPP_FROM = os.environ["TWILIO_WHATSAPP_FROM"]
GP_WHATSAPP_NUMBER = os.environ["GP_WHATSAPP_NUMBER"]

TIMEZONE = os.getenv("TIMEZONE", "America/Toronto")
