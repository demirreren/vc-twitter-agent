# Northside Ventures — Content Engine

Internal Slack bot that turns voice memos into structured Twitter/X content ideas. The GP receives rotating prompts via DM three times a week, replies with a voice memo, and the bot handles transcription, distribution to the team, and long-term logging.

## How It Works

```
Scheduler (Mon/Wed/Fri 9AM ET)
        │
        ▼
   GP receives DM prompt
        │
        ▼
   GP replies with voice memo
        │
        ▼
   Whisper transcription
        │
        ├──▶ #twitter channel (formatted post)
        │
        └──▶ Channel Canvas (running log)
```

- **Prompts rotate** through a curated list of 10 questions designed to surface original thinking — fund thesis, founder patterns, market takes, contrarian views.
- **Transcripts post to #twitter** so the social media manager can turn them into threads.
- **Every entry is appended to the channel Canvas** as a persistent, searchable content archive.

## Stack

| Component | Technology |
|---|---|
| Runtime | Python 3.11+ |
| Slack framework | Bolt for Python (Socket Mode) |
| Scheduling | APScheduler (cron) |
| Transcription | OpenAI Whisper API |
| Hosting | Railway |

## Project Structure

```
main.py              Entry point — scheduler + Bolt app
bot.py               Event handlers (voice memo DMs)
scheduler.py         Cron triggers for prompt delivery
transcribe.py        Whisper transcription
canvas_logger.py     Canvas create / append logic
prompts.py           Prompt rotation + state persistence
config.py            Environment variable loader
```

## Environment

Configured via `.env` locally or Railway dashboard variables in production. See `.env.example` for required keys.

| Variable | Description |
|---|---|
| `SLACK_BOT_TOKEN` | Bot OAuth token |
| `SLACK_APP_TOKEN` | App-level token (Socket Mode) |
| `GP_SLACK_USER_ID` | Slack user ID of the GP |
| `TWITTER_CHANNEL_ID` | Channel ID for #twitter |
| `OPENAI_API_KEY` | OpenAI API key (Whisper) |
| `TIMEZONE` | Scheduler timezone (default: `America/Toronto`) |

## Running

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python main.py
```

## Deployment

Connected to Railway via GitHub. The `Procfile` defines a worker process — no HTTP port needed. Socket Mode maintains the Slack connection.

## Slack App Scopes

`chat:write` · `im:write` · `im:history` · `files:read` · `canvases:write` · `canvases:read` · `channels:read` · `users:read`

Bot event subscription: `message.im`
