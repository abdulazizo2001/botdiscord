import os

DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN", "")
COMMAND_PREFIX = os.environ.get("COMMAND_PREFIX", "!")
STATE_FILE = os.environ.get("STATE_FILE", "state.json")
INACTIVITY_MINUTES = int(os.environ.get("INACTIVITY_MINUTES", "10"))

_mod_log = os.environ.get("MOD_LOG_CHANNEL_ID")
MOD_LOG_CHANNEL_ID = int(_mod_log) if _mod_log else None

CF_ACCOUNT_ID = os.environ.get("CF_ACCOUNT_ID", "")
CF_API_TOKEN = os.environ.get("CF_API_TOKEN", "")
