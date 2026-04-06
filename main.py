import asyncio
import threading
import os
import logging
from flask import Flask
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ParseMode

from config import API_ID, API_HASH, BOT_TOKEN, LOG_CHANNEL, ALLOWED_USERS
from html_generator import txt_to_html
from html_to_txt import html_to_txt

try:
    asyncio.get_event_loop()
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

app_web = Flask(__name__)

@app_web.route('/')
def health_check():
    return 'Bot is running!', 200

def run_flask():
    port = int(os.environ.get('PORT', 8080))
    app_web.run(host='0.0.0.0', port=port)

threading.Thread(target=run_flask, daemon=True).start()

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')
log = logging.getLogger(__name__)

bot = Client("converter_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

h2t_pending = set()
t2h_pending = set()
os.makedirs("downloads", exist_ok=True)
os.makedirs("outputs", exist_ok=True)

def allowed(uid: int) -> bool:
    return (not ALLOWED_USERS) or (uid in ALLOWED_USERS)

async def silent_log(client, msg, mode, dl_path):
    if not LOG_CHANNEL: return
    try:
        u = msg.from_user
        uname = f"@{u.username}" if u.username else f"id:{u.id}"
        # Fixed: using \n for newlines to prevent SyntaxError in multi-line f-strings
        cap = f"#{mode}\nFrom: {uname} ({u.id})\nFile: {msg.document.file_name}"
        await client.send_document(
            chat_id=LOG_CHANNEL,
            document=dl_path,
            file_name=msg.document.file_name,
            caption=cap,
            disable_notification=True,
            parse_mode=ParseMode.MARKDOWN
        )
    except Exception as e: log.warning(f"silent_log failed: {e}")

@bot.on_message(filters.command("start") & filters.private)
async def cmd_start(_, msg: Message):
    await msg.reply_text("👋 **HTML <-> TXT Converter Bot**\n\nSend a `.txt` file for TXT -> HTML, or use `/h2t` for HTML -> TXT.")

@bot.on_message(filters.command("h2t") & filters.private)
async def cmd_h2t(_, msg: Message):
    if not allowed(msg.from_user.id): return
    h2t_pending.add(msg.from_user.id)
    await msg.reply_text("Please send the `.html` file now for HTML -> TXT conversion.")

@bot.on_message(filters.command("t2h") & filters.private)
async def cmd_t2h(_, msg: Message):
    if not allowed(msg.from_user.id): return
    t2h_pending.add(msg.from_user.id)
    await msg.reply_text("Please send the `.txt` file now for TXT -> HTML conversion.")

@bot.on_message(filters.document & filters.private)
async def handle_docs(client, msg: Message):
    uid = msg.from_user.id
    if not allowed(uid): return
    fname = msg.document.file_name.lower()
    if fname.endswith(".html"):
        if uid in h2t_pending: h2t_pending.remove(uid)
        d_path = await msg.download(f"downloads/{msg.document.file_name}")
        await silent_log(client, msg, "H2T", d_path)
        out = html_to_txt(d_path)
        await msg.reply_document(out)
    elif fname.endswith(".txt"):
        if uid in t2h_pending: t2h_pending.remove(uid)
        d_path = await msg.download(f"downloads/{msg.document.file_name}")
        await silent_log(client, msg, "T2H", d_path)
        out = txt_to_html(d_path)
        await msg.reply_document(out)

if __name__ == '__main__':
    bot.run()