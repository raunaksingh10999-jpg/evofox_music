from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from database import add_user, user_exists, total_users
from config import BOT_USERNAME, OWNER_USERNAME

# --- Start image (replace with your own telegra.ph image) ---
START_IMAGE = "https://telegra.ph/file/your-music-image.jpg"

# --- Start caption ---
START_CAPTION = """
🎵 **Welcome to Music Bot!**

_Your ultimate music companion on Telegram_ 🎧

━━━━━━━━━━━━━━━━━━━
🔥 **Features:**
├ 🎶 Play any song instantly
├ 📋 Queue multiple songs  
├ ⏭️ Skip · Pause · Resume
└ 🔊 Crystal clear audio

━━━━━━━━━━━━━━━━━━━
💡 Use `/play <song name>` in a group
"""

# --- Inline buttons layout ---
# Row 1: 1 button
# Row 2: 2 buttons
# Row 3: 1 button
def get_start_buttons() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        # Row 1
        [
            InlineKeyboardButton("🎧 Play Music", callback_data="cb_play")
        ],
        # Row 2
        [
            InlineKeyboardButton("📚 Help", callback_data="cb_help"),
            InlineKeyboardButton("👤 Owner", url=f"https://t.me/{OWNER_USERNAME}")
        ],
        # Row 3
        [
            InlineKeyboardButton("➕ Add Me to Group", url=f"https://t.me/{BOT_USERNAME}?startgroup=true")
        ]
    ])

# --- Register handlers on the app ---
def register_start_handler(app):

    @app.on_message(filters.command("start") & filters.private)
    async def start_command(client, message: Message):
        user = message.from_user

        # Save user to database if new
        if not user_exists(user.id):
            add_user(
                user_id=user.id,
                username=user.username or "N/A",
                first_name=user.first_name or "N/A"
            )

        # Send photo with caption and buttons
        await message.reply_photo(
            photo=START_IMAGE,
            caption=START_CAPTION,
            reply_markup=get_start_buttons()
        )

    # --- Callback: Play Music ---
    @app.on_callback_query(filters.regex("cb_play"))
    async def cb_play(client, callback_query: CallbackQuery):
        await callback_query.answer(
            "Add me to a group, start Voice Chat, then use /play 🎶",
            show_alert=True
        )

    # --- Callback: Help ---
    @app.on_callback_query(filters.regex("cb_help"))
    async def cb_help(client, callback_query: CallbackQuery):
        help_text = """
🎵 **Commands List**

━━━━━━━━━━━━━━━━━━━
🎶 **Music**
├ `/play <song>` — Play a song
├ `/pause` — Pause playback
├ `/resume` — Resume playback
├ `/skip` — Skip current song
└ `/stop` — Stop & leave

📋 **Queue**
└ `/queue` — View song queue

━━━━━━━━━━━━━━━━━━━
_All commands work in groups only_ 💡
"""
        await callback_query.message.edit_caption(
            caption=help_text,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back", callback_data="cb_back")]
            ])
        )
        await callback_query.answer()

    # --- Callback: Back to Start ---
    @app.on_callback_query(filters.regex("cb_back"))
    async def cb_back(client, callback_query: CallbackQuery):
        await callback_query.message.edit_caption(
            caption=START_CAPTION,
            reply_markup=get_start_buttons()
        )
        await callback_query.answer()
