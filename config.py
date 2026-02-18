"""
Loads all environment variables from .env (locally) or from the
hosting platform's environment (Railway in production).
"""

import os
from dotenv import load_dotenv

load_dotenv()

SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
SLACK_APP_TOKEN = os.environ["SLACK_APP_TOKEN"]
GP_SLACK_USER_ID = os.environ["GP_SLACK_USER_ID"]
TWITTER_CHANNEL_ID = os.environ["TWITTER_CHANNEL_ID"]
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
TIMEZONE = os.getenv("TIMEZONE", "America/Toronto")
