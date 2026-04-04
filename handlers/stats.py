import asyncio
from pyrogram import filters
from pyrogram.types import (
    Message, InlineKeyboardMarkup,
    InlineKeyboardButton, CallbackQuery
)
from database import total_users, total_groups
from config import SUDO_USERS, START_IMAGE

def register_stats_handler(app):

    # -----------------------------------------------
    # /stats command — only sudo users can use
    # -----------------------------------------------
    @app.on_message(filters.command("stats") & filters.user(SUDO_USERS))
    async def stats_command(client, message: Message):

        # Fetch counts from database
        users  = total_users()
        groups = total_groups()
        total  = users + groups

        caption = f"""
📊 **Bot Statistics**

━━━━━━━━━━━━━━━━━━━
👥 **Total Users**   : `{users}`
🏘️ **Total Groups**  : `{groups}`
🌐 **Total Reach**   : `{total}`
━━━━━━━━━━━━━━━━━━━

🤖 **Bot Status**    : ✅ Online
🔐 **Sudo Users**    : `{len(SUDO_USERS)}`
━━━━━━━━━━━━━━━━━━━
"""

        # Send stats photo with caption and close button
        stats_msg = await message.reply_photo(
            photo=START_IMAGE,
            caption=caption,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🗑 Close", callback_data=f"stats_close#{message.id}")]
            ])
        )

    # -----------------------------------------------
    # Close button — deletes both messages
    # -----------------------------------------------
    @app.on_callback_query(
        filters.regex(r"stats_close#(\d+)") & filters.user(SUDO_USERS)
    )
    async def stats_clo
