from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.errors import PeerIdInvalid, UsernameNotOccupied
from database.sudo_db import add_sudo, remove_sudo, is_sudo, get_all_sudos, total_sudos
from config import OWNER_ID

def register_sudo_handlers(app):

    # -----------------------------------------------
    # /addsudo command
    # -----------------------------------------------
    @app.on_message(filters.command("addsudo") & filters.user(OWNER_ID))
    async def add_sudo_cmd(client, message: Message):
        target_user = None

        if message.reply_to_message:
            target_user = message.reply_to_message.from_user
        elif len(message.command) > 1:
            identifier = message.command[1]
            try:
                target_user = await client.get_users(identifier)
            except (PeerIdInvalid, UsernameNotOccupied):
                return await message.reply("❌ User nahi mila!\n\nSahi ID ya @username do.")
            except Exception as e:
                return await message.reply(f"❌ Error: `{e}`")
        else:
            return await message.reply(
                "⚠️ **Usage:**\n\n"
                "├ Kisi ke message pe reply karke:\n"
                "│  `/addsudo`\n\n"
                "├ User ID se:\n"
                "│  `/addsudo 123456789`\n\n"
                "└ Username se:\n"
                "   `/addsudo @username`"
            )

        if target_user.id == OWNER_ID:
            return await message.reply("👑 Owner ko sudo bananey ki zaroorat nahi hai.")

        if is_sudo(target_user.id):
            return await message.reply(f"⚠️ **{target_user.mention}** pehle se sudo list mein hai.")

        await message.reply(
            f"⚠️ **Confirm Karo**\n\n"
            f"👤 **User**    : {target_user.mention}\n"
            f"🆔 **ID**      : `{target_user.id}`\n"
            f"👤 **Username**: @{target_user.username or 'N/A'}\n\n"
            f"Kya aap sach mein is user ko sudo list mein\n"
            f"add karna chahte hain?",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("✅ Haan Add Karo", callback_data=f"confirm_addsudo#{target_user.id}"),
                    InlineKeyboardButton("❌ Cancel", callback_data="cancel_addsudo")
                ]
            ])
        )

    # -----------------------------------------------
    # Callback: Confirm add sudo
    # -----------------------------------------------
    @app.on_callback_query(filters.regex(r"confirm_addsudo#(\d+)") & filters.user(OWNER_ID))
    async def confirm_addsudo(client, callback_query: CallbackQuery):
        user_id = int(callback_query.data.split("#")[1])

        if is_sudo(user_id):
            return await callback_query.answer("⚠️ Ye user pehle se sudo list mein hai!", show_alert=True)

        try:
            user = await client.get_users(user_id)
            username = user.username or "N/A"
            user_display = f"{user.mention}\n🆔 `{user_id}`"
        except Exception:
            username = "N/A"
            user_display = f"🆔 `{user_id}`"

        added = add_sudo(user_id, username, OWNER_ID)

        if added:
            await callback_query.message.edit_text(
                f"✅ **Sudo Successfully Added!**\n\n"
                f"👤 **User**: {user_display}\n\n"
                f"🔓 Ab ye user sudo commands use kar sakta hai.\n\n"
                f"📋 `/sudolist` se list check karein."
            )
        else:
            await callback_query.message.edit_text("❌ **Add nahi ho saka!**\n\nDobara try karo.")

        await callback_query.answer()

    # -----------------------------------------------
    # Callback: Cancel add sudo
    # -----------------------------------------------
    @app.on_callback_query(filters.regex("cancel_addsudo") & filters.user(OWNER_ID))
    async def cancel_addsudo(client, callback_query: CallbackQuery):
        await callback_query.message.edit_text("❌ **Add sudo cancel ho gaya.**")
        await callback_query.answer()

    # -----------------------------------------------
    # /remsudo command
    # -----------------------------------------------
    @app.on_message(filters.command("remsudo") & filters.user(OWNER_ID))
    async def rem_sudo_cmd(client, message: Message):
        target_user = None

        if message.reply_to_message:
            target_user = message.reply_to_message.from_user
        elif len(message.command) > 1:
            identifier = message.command[1]
            try:
                target_user = await client.get_users(identifier)
            except (PeerIdInvalid, UsernameNotOccupied):
                return await message.reply("❌ User nahi mila!\n\nSahi ID ya @username do.")
            except Exception as e:
                return await message.reply(f"❌ Error: `{e}`")
        else:
            return await message.reply(
                "⚠️ **Usage:**\n\n"
                "├ Kisi ke message pe reply karke:\n"
                "│  `/remsudo`\n\n"
                "├ User ID se:\n"
                "│  `/remsudo 123456789`\n\n"
                "└ Username se:\n"
                "   `/remsudo @username`"
            )

        if target_user.id == OWNER_ID:
            return await message.reply("❌ **Owner ko sudo list se remove nahi kar sakte!\n\n**👑 Owner hamesha sudo rahega.")

        if not is_sudo(target_user.id):
            return await message.reply(f"⚠️ **{target_user.mention}** sudo list mein hai hi nahi!\n\n📋 `/sudolist` se check karo.")

        await message.reply(
            f"⚠️ **Confirm Karo**\n\n"
            f"👤 **User**    : {target_user.mention}\n"
            f"🆔 **ID**      : `{target_user.id}`\n"
            f"👤 **Username**: @{target_user.username or 'N/A'}\n\n"
            f"Kya aap sach mein is user ko sudo list se\n"
            f"remove karna chahte hain?",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("✅ Haan Remove Karo", callback_data=f"confirm_remsudo#{target_user.id}"),
                    InlineKeyboardButton("❌ Cancel", callback_data="cancel_remsudo")
                ]
            ])
        )

    # -----------------------------------------------
    # Callback: Confirm remove sudo
    # -----------------------------------------------
    @app.on_callback_query(filters.regex(r"confirm_remsudo#(\d+)") & filters.user(OWNER_ID))
    async def confirm_remsudo(client, callback_query: CallbackQuery):
        user_id = int(callback_query.data.split("#")[1])

        if not is_sudo(user_id):
            return await callback_query.answer("⚠️ Ye user pehle se sudo list mein nahi hai!", show_alert=True)

        removed = remove_sudo(user_id)

        if removed:
            try:
                user = await client.get_users(user_id)
                user_display = f"{user.mention}\n🆔 `{user_id}`"
            except Exception:
                user_display = f"🆔 `{user_id}`"

            await callback_query.message.edit_text(
                f"✅ **Sudo Successfully Removed!**\n\n"
                f"👤 **User**: {user_display}\n\n"
                f"🔓 Ab ye user sudo commands use nahi kar sakta.\n\n"
                f"📋 `/sudolist` se list check karo."
            )
        else:
            await callback_query.message.edit_text("❌ **Remove nahi ho saka!**\n\nDobara try karo.")
        await callback_query.answer()

    # -----------------------------------------------
    # Callback: Cancel remove sudo
    # -----------------------------------------------
    @app.on_callback_query(filters.regex("cancel_remsudo") & filters.user(OWNER_ID))
    async def cancel_remsudo(client, callback_query: CallbackQuery):
        await callback_query.message.edit_text("❌ **Remove cancel ho gaya.**\n\nUser sudo list mein safe hai. ✅")
        await callback_query.answer()

    # -----------------------------------------------
    # /sudolist command
    # -----------------------------------------------
    @app.on_message(filters.command("sudolist") & filters.user(OWNER_ID))
    async def sudolist_cmd(client, message: Message):
        sudos = get_all_sudos()

        if not sudos:
            return await message.reply("📋 **Sudo Users List:**\n\nAbhi tak koi sudo user add nahi kiya gaya hai.\n`/addsudo` se add karein.")

        text = f"📋 **Sudo Users List ({total_sudos()}):**\n\n"
        for user in sudos:
            username_display = f" (@{user['username']})" if user['username'] != "N/A" else ""
            text += f"👤 `{user['user_id']}`{username_display}\n"
            text += f"📅 Added At: `{user['added_at']}`\n\n"

        await message.reply(text)
