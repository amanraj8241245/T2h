import os

# Load from environment variables (set these in Render dashboard)
API_ID = int(os.environ.get("API_ID", "36123528"))
API_HASH = os.environ.get("API_HASH", "7f77eb79febe2b7cf5d33d6d57bc8ac0")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8564887159:AAFk2GpNH96K_G0Vm1CfoOX3EX0GBWzeKoQ")
LOG_CHANNEL = int(os.environ.get("LOG_CHANNEL", "-1003891933514"))

# Optional: comma-separated user IDs allowed to use bot
# Leave empty or unset for open access
_allowed = os.environ.get("ALLOWED_USERS", "")
ALLOWED_USERS = [int(x.strip()) for x in _allowed.split(",") if x.strip().isdigit()]
