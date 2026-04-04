import asyncio
from pyrogram import filters
from pyrogram.types import (
    Message, InlineKeyboardMarkup, 
    InlineKeyboardButton, CallbackQuery
)
from pyrogram.errors import (
    FloodWait, UserIsBlocked, 
    InputUserDeactivated, ChatWriteForbidden,
    PeerIdInvalid
)
from database import get_all_users, get_all_groups
from config import OWNER_ID

# --- Broadcast state store ---
# Stores the message to broadcast temporarily
broadcast_cache = {}

def register_broadcast_handler(app):

    # -----------------------------------------------
    # Step 1: Owner sends /broadcast
    # Bot asks: forward or type the message to send
    # -----------------------------------------------
    @app.on_message(filters.command("broadcast") & filters.user(OWNER_ID))
    async def broadcast_start(client, message: Message):
        broadcast_cache[OWNER_ID] = {"step": "waiting"}
        await message.reply(
            "📢 **Broadcast Mode On**\n\n"
            "Ab jo message aap next bhejenge\n"
            "wo **users + groups** ko broadcast hoga.\n\n"
            "✅ Support karta hai:\n"
            "├ 📝 Text message\n"
            "├ 🖼 Photo + Caption\n"
            "├ 🔘 Inline Buttons _(auto copy honge)_\n\n"
            "❌ Cancel karne ke liye `/cancel` bhejo",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("❌ Cancel", callback_data="bc_cancel")]
            ])
        )

    # -----------------------------------------------
    # Step 2: Owner sends the actual message to broadcast
    # -----------------------------------------------
    @app.on_message(filters.private & filters.user(OWNER_ID))
    async def receive_broadcast_message(client, message: Message):

        # Ignore if not in broadcast waiting state
        if broadcast_cache.get(OWNER_ID, {}).get("step") != "waiting":
            return

        # Ignore /commands
        if message.text and message.text.startswith("/"):
            return

        # Save message to cache
        broadcast_cache[OWNER_ID] = {
            "step": "confirm",
            "message": message
        }

        # Show preview + confirm buttons
        await message.reply(
            "👀 **Preview dekh lo — yahi broadcast hoga:**\n\n"
            "Confirm karo ya cancel karo 👇",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("✅ Broadcast Karo", callback_data="bc_confirm"),
                    InlineKeyboardButton("❌ Cancel", callback_data="bc_cancel")
                ]
            ])
        )

    # -----------------------------------------------
    # Callback: Cancel broadcast
    # -----------------------------------------------
    @app.on_callback_query(filters.regex("bc_cancel") & filters.user(OWNER_ID))
    async def bc_cancel(client, callback_query: CallbackQuery):
        broadcast_cache.pop(OWNER_ID, None)
        await callback_query.message.edit_text(
            "❌ **Broadcast cancel ho gaya.**"
        )

    # -----------------------------------------------
    # Callback: Confirm and start broadcasting
    # -----------------------------------------------
    @app.on_callback_query(filters.regex("bc_confirm") & filters.user(OWNER_ID))
    async def bc_confirm(client, callback_query: CallbackQuery):

        data = broadcast_cache.get(OWNER_ID, {})
        if data.get("step") != "confirm":
            await callback_query.answer("Koi message nahi mila!", show_alert=True)
            return

        original_msg: Message = data["message"]
        broadcast_cache.pop(OWNER_ID, None)

        await callback_query.message.edit_text(
            "📤 **Broadcast shuru ho gaya...**\n"
            "Please wait ⏳"
        )

        # --- Fetch all users and groups from DB ---
        users  = get_all_users()
        groups = get_all_groups()
        all_targets = users + groups

        # --- Counters ---
        success = 0
        failed  = 0
        blocked = 0

        # --- Send to each target ---
        for target_id in all_targets:
            try:
                await forward_message(client, original_msg, target_id)
                success += 1

            except FloodWait as e:
                # Telegram rate limit — wait and retry
                await asyncio.sleep(e.value)
                try:
                    await forward_message(client, original_msg, target_id)
                    success += 1
                except Exception:
                    failed += 1

            except (UserIsBlocked, InputUserDeactivated):
                blocked += 1

            except (ChatWriteForbidden, PeerIdInvalid):
                failed += 1

            except Exception:
                failed += 1

            # Small delay to avoid flood
            await asyncio.sleep(0.05)

        # --- Final report to owner ---
        total = len(all_targets)
        await callback_query.message.reply(
            f"✅ **Broadcast Complete!**\n\n"
            f"👥 Total targets : `{total}`\n"
            f"✅ Bheja gaya    : `{success}`\n"
            f"🚫 Blocked       : `{blocked}`\n"
            f"❌ Failed        : `{failed}`\n\n"
            f"📊 Success rate  : `{round((success/total)*100, 1) if total else 0}%`"
        )

    # -----------------------------------------------
    # /cancel command shortcut
    # -----------------------------------------------
    @app.on_message(filters.command("cancel") & filters.user(OWNER_ID))
    async def cancel_command(client, message: Message):
        if OWNER_ID in broadcast_cache:
            broadcast_cache.pop(OWNER_ID, None)
            await message.reply("❌ **Broadcast cancel ho gaya.**")
        else:
            await message.reply("Koi active broadcast nahi tha.")


# -----------------------------------------------
# Helper: Forward any type of message
# Supports text, photo+caption, buttons
# -----------------------------------------------
async def forward_message(client, original_msg: Message, target_id: int):
    """
    Copies message to target preserving:
    - Text / Caption
    - Photo
    - Inline buttons (reply_markup)
    """
    markup = original_msg.reply_markup or None

    # Photo + Caption
    if original_msg.photo:
        await client.send_photo(
            chat_id=target_id,
            photo=original_msg.photo.file_id,
            caption=original_msg.caption or "",
            reply_markup=markup
        )

    # Text only
    elif original_msg.text:
        await client.send_message(
            chat_id=target_id,
            text=original_msg.text,
            reply_markup=markup
        )

    # Video + Caption
    elif original_msg.video:
        await client.send_video(
            chat_id=target_id,
            video=original_msg.video.file_id,
            caption=original_msg.caption or "",
            reply_markup=markup
        )

    # Document + Caption
    elif original_msg.document:
        await client.send_document(
            chat_id=target_id,
            document=original_msg.document.file_id,
            caption=original_msg.caption or "",
            reply_markup=markup
        )

    # Sticker
    elif original_msg.sticker:
        await client.send_sticker(
            chat_id=target_id,
            sticker=original_msg.sticker.file_id
        )
