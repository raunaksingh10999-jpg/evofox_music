from pyrogram import Client, filters
from pyrogram.types import Message
from pytgcalls import PyTgCalls
from pytgcalls.types import MediaStream
from pytgcalls.types.stream import StreamAudioQuality
import yt_dlp, asyncio
from config import API_ID, API_HASH, STRING_SESSION

# --- Client setup ---
app = Client(
    "music_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=STRING_SESSION
)
call_py = PyTgCalls(app)

# --- Queue per chat ---
queues = {}

# --- YouTube audio fetcher ---
def fetch_audio(query: str):
    ydl_opts = {
        "format": "bestaudio/best",
        "quiet": True,
        "default_search": "ytsearch",
        "noplaylist": True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(query, download=False)
        if "entries" in info:
            info = info["entries"][0]
        return info["url"], info["title"]

# --- Play next in queue ---
async def play_next(chat_id: int):
    if chat_id in queues and queues[chat_id]:
        url, title = queues[chat_id].pop(0)
        await call_py.change_stream(chat_id, MediaStream(url))
        return title
    else:
        await call_py.leave_group_call(chat_id)
        return None

# --- /play command ---
@app.on_message(filters.command("play") & filters.group)
async def play(client: Client, message: Message):
    if len(message.command) < 2:
        await message.reply("Usage: `/play song name or YouTube URL`")
        return

    query = " ".join(message.command[1:])
    msg = await message.reply("🔍 Searching...")

    try:
        url, title = fetch_audio(query)
    except Exception as e:
        await msg.edit(f"❌ Error fetching audio: {e}")
        return

    chat_id = message.chat.id

    try:
        await call_py.join_group_call(chat_id, MediaStream(url))
        await msg.edit(f"▶️ Now playing: **{title}**")
    except Exception:
        # Already in a call — add to queue
        if chat_id not in queues:
            queues[chat_id] = []
        queues[chat_id].append((url, title))
        await msg.edit(f"➕ Added to queue: **{title}**\nPosition: {len(queues[chat_id])}")

# --- /skip command ---
@app.on_message(filters.command("skip") & filters.group)
async def skip(client: Client, message: Message):
    chat_id = message.chat.id
    title = await play_next(chat_id)
    if title:
        await message.reply(f"⏭️ Skipped! Now playing: **{title}**")
    else:
        await message.reply("⏹️ Queue empty. Left voice chat.")

# --- /pause command ---
@app.on_message(filters.command("pause") & filters.group)
async def pause(client: Client, message: Message):
    await call_py.pause_stream(message.chat.id)
    await message.reply("⏸️ Paused.")

# --- /resume command ---
@app.on_message(filters.command("resume") & filters.group)
async def resume(client: Client, message: Message):
    await call_py.resume_stream(message.chat.id)
    await message.reply("▶️ Resumed.")

# --- /stop command ---
@app.on_message(filters.command("stop") & filters.group)
async def stop(client: Client, message: Message):
    chat_id = message.chat.id
    queues.pop(chat_id, None)
    await call_py.leave_group_call(chat_id)
    await message.reply("⏹️ Stopped and left voice chat.")

# --- /queue command ---
@app.on_message(filters.command("queue") & filters.group)
async def show_queue(client: Client, message: Message):
    chat_id = message.chat.id
    q = queues.get(chat_id, [])
    if not q:
        await message.reply("📭 Queue is empty.")
        return
    text = "📋 **Queue:**\n"
    for i, (_, title) in enumerate(q, 1):
        text += f"{i}. {title}\n"
    await message.reply(text)

# --- Stream ended handler ---
@call_py.on_stream_end()
async def stream_end(client, update):
    chat_id = update.chat_id
    title = await play_next(chat_id)
    if title:
        await app.send_message(chat_id, f"▶️ Now playing: **{title}**")

# --- Register Handlers ---
import importlib
handlers_to_load = [
    ("handlers.start", "register_start_handler"),
    ("handlers.stats", "register_stats_handler"),
    ("handlers.sudo", "register_sudo_handlers"),
    ("handlers.broadcast", "register_broadcast_handler"),
    ("handlers.blacklist", "register_blacklist_handlers")
]

for module_name, func_name in handlers_to_load:
    try:
        mod = importlib.import_module(module_name)
        func = getattr(mod, func_name)
        func(app)
    except Exception as e:
        print(f"Failed to load {module_name}: {e}")

# --- Run ---
call_py.start()
app.run()
