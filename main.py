from flask import Flask
import threading
import os
import logging
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ParseMode

from config import API_ID, API_HASH, BOT_TOKEN, LOG_CHANNEL, ALLOWED_USERS
from html_generator import txt_to_html
from html_to_txt import html_to_txt

# -- Web Server for Render --
app_web = Flask(__name__)
@app_web.route('/')
def health_check():
    return 'Bot is running!', 200

def run_flask():
    port = int(os.environ.get('PORT', 8080))
    app_web.run(host='0.0.0.0', port=port)

threading.Thread(target=run_flask, daemon=True).start()

# -- Bot Logic --
logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')
log = logging.getLogger(__name__)

bot = Client("converter_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

h2t_pending = set()
os.makedirs("downloads", exist_ok=True)
os.makedirs("outputs", exist_ok=True)

def allowed(uid: int) -> bool:
    return (not ALLOWED_USERS) or (uid in ALLOWED_USERS)

async def silent_log(client, msg, mode, dl_path):
    if not LOG_CHANNEL: return
    try:
        u = msg.from_user
        uname = f"@{u.username}" if u.username else f"id:{u.id}"
        # Fixed the multiline f-string syntax error here
        caption_text = f"#{mode}
From: {uname} ({u.id})
File: {msg.document.file_name}"
        await client.send_document(
            chat_id=LOG_CHANNEL,
            document=dl_path,
            file_name=msg.document.file_name,
            caption=caption_text,
            disable_notification=True,
            parse_mode=ParseMode.MARKDOWN
        )
    except Exception as e: log.warning(f"silent_log failed: {e}")

@bot.on_message(filters.command("start") & filters.private)
async def cmd_start(_, msg: Message):
    await msg.reply_text("👋 **HTML <-> TXT Converter Bot**

Send a `.txt` file to convert to HTML, or use `/h2t` for HTML to TXT.")

@bot.on_message(filters.command("h2t") & filters.private)
async def cmd_h2t(_, msg: Message):
    if not allowed(msg.from_user.id): return
    h2t_pending.add(msg.from_user.id)
    await msg.reply_text("Please send the `.html` file now.")

@bot.on_message(filters.document & filters.private)
async def handle_docs(client, msg: Message):
    if not allowed(msg.from_user.id): return
    fname = msg.document.file_name.lower()

    if fname.endswith(".html") and msg.from_user.id in h2t_pending:
        h2t_pending.remove(msg.from_user.id)
        d_path = await msg.download(f"downloads/{msg.document.file_name}")
        await silent_log(client, msg, "H2T", d_path)
        out = html_to_txt(d_path)
        await msg.reply_document(out)
    elif fname.endswith(".txt"):
        d_path = await msg.download(f"downloads/{msg.document.file_name}")
        await silent_log(client, msg, "T2H", d_path)
        out = txt_to_html(d_path)
        await msg.reply_document(out)

print("Bot is starting...")
bot.run()
