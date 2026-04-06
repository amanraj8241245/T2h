import os

# Load from environment variables (set these in Render dashboard)
API_ID = int(os.environ.get("API_ID", "0"))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
LOG_CHANNEL = int(os.environ.get("LOG_CHANNEL", "0"))

# Optional: comma-separated user IDs allowed to use bot
# Leave empty or unset for open access
_allowed = os.environ.get("ALLOWED_USERS", "")
ALLOWED_USERS = [int(x.strip()) for x in _allowed.split(",") if x.strip().isdigit()]
