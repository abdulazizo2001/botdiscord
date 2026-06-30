import os

DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN", "")
COMMAND_PREFIX = os.environ.get("COMMAND_PREFIX", "!")
STATE_FILE = os.environ.get("STATE_FILE", "state.json")
INACTIVITY_MINUTES = int(os.environ.get("INACTIVITY_MINUTES", "10"))

_mod_log = os.environ.get("MOD_LOG_CHANNEL_ID")
MOD_LOG_CHANNEL_ID = int(_mod_log) if _mod_log else None

MISTRAL_API_KEY = os.environ.get("MISTRAL_API_KEY", "")
