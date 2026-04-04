# -----------------------------------------------
    # /remsudo command
    # Usage:
    #   Reply to user's message: /remsudo
    #   By user ID:              /remsudo 123456789
    #   By username:             /remsudo @username
    # -----------------------------------------------
    @app.on_message(filters.command("remsudo") & filters.user(OWNER_ID))
    async def rem_sudo_cmd(client, message: Message):

        target_user = None

        # --- Method 1: Reply to a message ---
        if message.reply_to_message:
            target_user = message.reply_to_message.from_user

        # --- Method 2: User ID or @username given ---
        elif len(message.command) > 1:
            identifier = message.command[1]
            try:
                user = await client.get_users(identifier)
                target_user = user
            except (PeerIdInvalid, UsernameNotOccupied):
                await message.reply(
                    "❌ **User nahi mila!**\n\n"
                    "Sahi ID ya @username do."
                )
                return
            except Exception as e:
                await message.reply(f"❌ Error: `{e}`")
                return

        # --- No input given ---
        else:
            await message.reply(
                "⚠️ **Usage:**\n\n"
                "├ Kisi ke message pe reply karke:\n"
                "│  `/remsudo`\n\n"
                "├ User ID se:\n"
                "│  `/remsudo 123456789`\n\n"
                "└ Username se:\n"
                "   `/remsudo @username`"
            )
            return

        # --- Cannot remove owner ---
        if target_user.id == OWNER_ID:
            await message.reply(
                "❌ **Owner ko sudo list se remove nahi kar sakte!\n\n**"
                "👑 Owner hamesha sudo rahega."
            )
            return

        # --- Check if user is in sudo list ---
        if not is_sudo(target_user.id):
            await message.reply(
                f"⚠️ **{target_user.mention}** sudo list mein hai hi nahi!\n\n"
                f"📋 `/sudolist` se check karo."
            )
            return

        # --- Confirm before removing ---
        await message.reply(
            f"⚠️ **Confirm Karo**\n\n"
            f"👤 **User**    : {target_user.mention}\n"
            f"🆔 **ID**      : `{target_user.id}`\n"
            f"👤 **Username**: @{target_user.username or 'N/A'}\n\n"
            f"Kya aap sach mein is user ko sudo list se\n"
            f"remove karna chahte hain?",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        "✅ Haan Remove Karo",
                        callback_data=f"confirm_remsudo#{target_user.id}"
                    ),
                    InlineKeyboardButton(
                        "❌ Cancel",
                        callback_data="cancel_remsudo"
                    )
                ]
            ])
        )

    # -----------------------------------------------
    # Callback: Confirm remove sudo
    # -----------------------------------------------
    @app.on_callback_query(
        filters.regex(r"confirm_remsudo#(\d+)") & filters.user(OWNER_ID)
    )
    async def confirm_remsudo(client, callback_query: CallbackQuery):
        user_id = int(callback_query.data.split("#")[1])

        # Double check — still in sudo list?
        if not is_sudo(user_id):
            await callback_query.message.edit_text(
                "⚠️ Ye user pehle se sudo list mein nahi hai!"
            )
            await callback_query.answer()
            return

        # Remove from database
        removed = remove_sudo(user_id)

        if removed:
            # Try to get user info for display
            try:
                user = await client.get_users(user_id)
                user_display = f"{user.mention}\n🆔 `{user_id}`"
            except Exception:
                user_display = f"🆔 `{user_id}`"

            await callback_query.message.edit_text(
                f"✅ **Sudo Successfully Removed!**\n\n"
                f"👤 **User**  : {user_display}\n\n"
                f"🔓 Ab ye user sudo commands\n"
                f"use nahi kar sakta.\n\n"
                f"📋 Updated list dekhne ke liye\n"
                f"`/sudolist` use karo."
            )
        else:
            await callback_query.message.edit_text(
                "❌ **Remove nahi ho saka!**\n\n"
                "Dobara try karo."
            )

        await callback_query.answer()

    # -----------------------------------------------
    # Callback: Cancel remove sudo
    # -----------------------------------------------
    @app.on_callback_query(
        filters.regex("cancel_remsudo") & filters.user(OWNER_ID)
    )
    async def cancel_remsudo(client, callback_query: CallbackQuery):
        await callback_query.message.edit_text(
            "❌ **Remove cancel ho gaya.**\n\n"
            "User sudo list mein safe hai. ✅"
        )
        await callback_query.answer()
