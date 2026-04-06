import os

API_ID      = int(os.environ.get("API_ID", 0))
API_HASH    = os.environ.get("API_HASH", "")
BOT_TOKEN   = os.environ.get("BOT_TOKEN", "")

# Numeric ID of log channel  e.g. -1001234567890
# Bot must be ADMIN in that channel
LOG_CHANNEL = int(os.environ.get("LOG_CHANNEL", 0))

# Leave [] to allow everyone
ALLOWED_USERS: list[int] = []
