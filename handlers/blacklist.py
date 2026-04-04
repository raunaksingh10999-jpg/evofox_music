from pyrogram import filters
from pyrogram.types import Message
from config import OWNER_ID
from database.sudo_db import is_sudo
from database.blacklist_db import add_bl_chat, get_all_bl_chats

def register_blacklist_handlers(app):

    # Custom filter to check if user is Owner or Sudo
    async def is_sudo_or_owner_filter(_, __, message: Message):
        user_id = getattr(message.from_user, "id", 0)
        if user_id == OWNER_ID:
            return True
        return is_sudo(user_id)
        
    sudo_filter = filters.create(is_sudo_or_owner_filter)

    # -----------------------------------------------
    # /addblchat command
    # -----------------------------------------------
    @app.on_message(filters.command("addblchat") & sudo_filter)
    async def add_bl_chat_cmd(client, message: Message):
        if len(message.command) < 2:
            return await message.reply("⚠️ **Usage:**\n`/addblchat <chat_id>`")
            
        chat_id_str = message.command[1]
        try:
            chat_id = int(chat_id_str)
        except ValueError:
            return await message.reply("❌ **Invalid Chat ID!** Use numbers only.")
            
        # Try to leave the chat if the bot is in it
        try:
            await client.leave_chat(chat_id)
            left_status = "✅ Bot has successfully left the group."
        except Exception as e:
            # It might fail if the bot is not in the group, which is fine
            left_status = "⚠️ Bot was not in the group, or couldn't leave."

        # Add to database
        added = add_bl_chat(chat_id)
        
        if added:
            await message.reply(
                f"✅ **Chat Blacklisted Successfully!**\n\n"
                f"🆔 **Chat ID:** `{chat_id}`\n"
                f"ℹ️ {left_status}"
            )
        else:
            await message.reply(
                f"⚠️ **Chat is already blacklisted!**\n\n"
                f"🆔 **Chat ID:** `{chat_id}`\n"
                f"ℹ️ {left_status}"
            )

    # -----------------------------------------------
    # /allblchats command
    # -----------------------------------------------
    @app.on_message(filters.command("allblchats") & sudo_filter)
    async def all_bl_chats_cmd(client, message: Message):
        bl_chats = get_all_bl_chats()
        
        if not bl_chats:
            return await message.reply("📋 **Blacklisted Chats:**\n\nNo chats have been blacklisted yet.")
            
        text = f"📋 **Blacklisted Chats List ({len(bl_chats)}):**\n\n"
        for i, chat_id in enumerate(bl_chats, 1):
            text += f"**{i}.** `{chat_id}`\n"
            
        await message.reply(text)

