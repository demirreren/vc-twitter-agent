# Northside Ventures — Twitter/X Content Bot

A Slack bot that helps the Northside Ventures GP consistently generate Twitter/X content ideas. It sends scheduled prompts, accepts voice memo replies, transcribes them with OpenAI Whisper, posts summaries to the **#twitter** channel, and maintains a running log in that channel's Canvas.

## How It Works

```
┌────────────┐  9 AM Mon/Wed/Fri  ┌─────────┐
│  Scheduler │ ──────────────────▶ │  GP DM  │
└────────────┘                     └────┬────┘
                                        │  GP replies with
                                        │  a voice memo
                                        ▼
                                  ┌───────────┐
                                  │  Whisper   │
                                  │ Transcribe │
                                  └─────┬─────┘
                                        │
                          ┌─────────────┼─────────────┐
                          ▼                           ▼
                   ┌─────────────┐          ┌────────────────┐
                   │  #twitter   │          │ Channel Canvas │
                   │   message   │          │  (append log)  │
                   └─────────────┘          └────────────────┘
```

1. **Scheduled prompt** — APScheduler sends a DM to the GP at 9:00 AM ET on Monday, Wednesday, and Friday with a rotating content prompt.
2. **Voice memo reply** — The GP records a Slack voice memo in that DM thread.
3. **Transcription** — The bot downloads the audio and transcribes it via OpenAI Whisper.
4. **#twitter post** — A formatted summary (prompt + transcript + date) is posted to the **#twitter** channel so the social media manager can see it.
5. **Canvas log** — The same entry is appended to the **#twitter** channel's Canvas, creating the canvas automatically if it doesn't exist yet.

---

## Prerequisites

- Python 3.11+
- A Slack workspace where you can install apps
- An OpenAI API key (for Whisper transcription)

---

## 1. Create the Slack App

Go to [https://api.slack.com/apps](https://api.slack.com/apps) and click **Create New App → From scratch**.

### a) Bot Token Scopes

Navigate to **OAuth & Permissions → Scopes → Bot Token Scopes** and add:

| Scope | Purpose |
|---|---|
| `chat:write` | Post messages to channels and DMs |
| `im:write` | Open DM conversations with the GP |
| `im:history` | Read DM messages (to receive voice memos) |
| `files:read` | Download voice memo files |
| `canvases:write` | Create and edit channel canvases |
| `canvases:read` | Check if a canvas already exists |
| `channels:read` | Read channel info (needed for `conversations.info`) |
| `users:read` | Resolve user info |

### b) Enable Socket Mode

1. Go to **Settings → Socket Mode** and toggle it **on**.
2. You'll be prompted to generate an **App-Level Token** — give it the `connections:write` scope.
3. Copy this token (starts with `xapp-`) — this is your `SLACK_APP_TOKEN`.

### c) Event Subscriptions

1. Go to **Features → Event Subscriptions** and toggle **on**.
2. Under **Subscribe to bot events**, add:
   - `message.im` — so the bot receives DMs from the GP.
3. Save changes.

### d) Install the App

1. Go to **Settings → Install App** and click **Install to Workspace**.
2. Authorize the requested permissions.
3. Copy the **Bot User OAuth Token** (starts with `xoxb-`) — this is your `SLACK_BOT_TOKEN`.

---

## 2. Gather IDs

### GP's Slack User ID

1. Open Slack and go to the GP's profile.
2. Click the **three dots (⋯)** menu.
3. Select **Copy member ID**.
4. This is your `GP_SLACK_USER_ID` (e.g., `U012AB3CD`).

### #twitter Channel ID

1. Right-click the **#twitter** channel in the sidebar.
2. Select **View channel details**.
3. Scroll to the bottom — the Channel ID is shown there (e.g., `C012AB3CD`).
4. This is your `TWITTER_CHANNEL_ID`.

> **Important:** Make sure the bot is a member of the **#twitter** channel. Invite it with `/invite @YourBotName` in the channel.

---

## 3. Environment Variables

Copy the example file and fill in your values:

```bash
cp .env.example .env
```

| Variable | Description |
|---|---|
| `SLACK_BOT_TOKEN` | Bot OAuth token (`xoxb-…`) |
| `SLACK_APP_TOKEN` | App-level token for Socket Mode (`xapp-…`) |
| `GP_SLACK_USER_ID` | Slack user ID of the GP |
| `TWITTER_CHANNEL_ID` | Channel ID of #twitter |
| `OPENAI_API_KEY` | OpenAI API key for Whisper |
| `TIMEZONE` | Timezone for the scheduler (default: `America/Toronto`) |

---

## 4. Run Locally

```bash
# Create a virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the bot
python main.py
```

You should see output like:

```
[...] [main] Starting Northside Ventures Slack Bot…
[...] [scheduler] Scheduler started — next run: 2026-02-20 09:00:00-05:00
[...] [main] Connecting to Slack via Socket Mode…
```

---

## 5. Deploy to Railway

1. Push this repo to GitHub.
2. Go to [railway.app](https://railway.app) and create a new project.
3. Select **Deploy from GitHub repo** and connect this repository.
4. Railway will detect the `Procfile` and run `python main.py` as a worker.
5. Go to **Variables** in the Railway dashboard and add all six environment variables from the table above.
6. Deploy. The bot will start immediately.

> **Note:** Railway's worker process type (defined in `Procfile`) runs continuously without needing an HTTP port. Socket Mode handles the Slack connection.

---

## 6. Canvas Log

The bot automatically maintains a Canvas attached to the **#twitter** channel.

### Where to find it

1. Open the **#twitter** channel in Slack.
2. Click the **Canvas** icon in the channel header (bookmark bar area) — or look for the canvas in the channel's tab bar.

### What it looks like

The canvas contains a running log with entries like:

```
## February 18, 2026
**Prompt:** What's one thing a founder said to you this week that genuinely surprised you?

**Transcript:**
This week I was talking to a founder building in the climate space and she said something
that really stuck with me...

---
```

The bot creates the canvas on the first voice memo if one doesn't already exist, and appends to it on every subsequent memo.

---

## Project Structure

```
├── main.py              # Entry point — starts scheduler + Slack Bolt app
├── bot.py               # Slack event handlers (voice memo DMs)
├── scheduler.py         # APScheduler — sends prompts Mon/Wed/Fri at 9 AM ET
├── transcribe.py        # OpenAI Whisper transcription
├── canvas_logger.py     # Slack Canvas create/edit logic
├── prompts.py           # Rotating prompt list + JSON state tracker
├── config.py            # Loads env vars via python-dotenv
├── requirements.txt     # Pinned dependencies
├── .env.example         # Template for required env vars
├── Procfile             # Railway: worker process
└── README.md            # This file
```

---

## Troubleshooting

| Problem | Solution |
|---|---|
| Bot doesn't respond to voice memos | Make sure `message.im` event subscription is enabled and the bot is running in Socket Mode |
| "not_in_channel" error when posting | Invite the bot to #twitter with `/invite @YourBotName` |
| Canvas creation fails | Verify `canvases:write` and `canvases:read` scopes are added and the app is reinstalled |
| Scheduler doesn't fire | Check that `TIMEZONE` is set correctly (default: `America/Toronto`) |
| Voice memo download fails | Ensure `files:read` scope is granted — the bot needs this to access uploaded files |
| "missing_scope" error | Add the missing scope in the Slack App dashboard, then **reinstall** the app to your workspace |
