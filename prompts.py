import json
import os

PROMPTS = [
    "What's one thing a founder said to you this week that genuinely surprised you?",
    "What's a deal you passed on recently — and what was your gut reason?",
    "What do you believe about Canadian startups that most people get wrong?",
    "What's a trend you're excited about that nobody is talking about yet?",
    "What's the most common mistake you're seeing pre-seed founders make right now?",
    "What's something that changed your mind recently — about a market, a founder type, anything?",
    "What's a pattern you've noticed across multiple founder pitches this month?",
    "If you could give one piece of advice to a Canadian founder trying to break into the US market, what would it be?",
    "What's a narrative in VC Twitter right now that you disagree with?",
    "What's something about your investment thesis that's evolved since you started Northside?",
]

STATE_FILE = os.path.join(os.path.dirname(__file__), "prompt_state.json")


def _load_index() -> int:
    if not os.path.exists(STATE_FILE):
        return 0
    try:
        with open(STATE_FILE, "r") as f:
            return json.load(f).get("index", 0)
    except (json.JSONDecodeError, IOError):
        return 0


def _save_index(index: int) -> None:
    with open(STATE_FILE, "w") as f:
        json.dump({"index": index}, f)


def get_next_prompt() -> str:
    """Return the next prompt in rotation and advance the pointer."""
    idx = _load_index()
    prompt = PROMPTS[idx % len(PROMPTS)]
    _save_index((idx + 1) % len(PROMPTS))
    return prompt


def get_last_prompt() -> str:
    """Return the most recently sent prompt (one behind the current pointer)."""
    idx = (_load_index() - 1) % len(PROMPTS)
    return PROMPTS[idx]
