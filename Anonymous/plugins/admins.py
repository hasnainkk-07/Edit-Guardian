# (©) Anonymous Emperor 

from pyrogram import enums
from pyrogram.types import ChatPermissions
from pyrogram.errors.exceptions.bad_request_400 import ChatAdminRequired, UserAdminInvalid

import datetime
from Anonymous import app
from Anonymous.bot import handler
from Anonymous.helpers.filters import admin_filter as admin, bot_owner_filter as owner
from hydragram import filters, handler as bot

def mention(user, name, mention=True):
    if mention:
        return f"[{name}](tg://openmessage?user_id={user})"
    return f"[{name}](https://t.me/{user})"


async def get_userid_from_username(username):
    try:
        user = await app.get_users(username)
    except:
        return None
    return [user.id, user.first_name]


async def ban_user(chat_id, user_id, first_name, reason):
    try:
        await app.ban_chat_member(chat_id, user_id)
    except ChatAdminRequired:
        return "I don't have permission to ban members.", False
    except UserAdminInvalid:
        return "I can't ban an admin!", False
    except Exception as e:
        return f"Error: {e}", False

    user_mention = mention(user_id, first_name)
    message = f"{user_mention} was banned.\n"
    if reason:
        message += f"Reason: `{reason}`"
    return message, True


async def unban_user(chat_id, user_id, first_name):
    try:
        await app.unban_chat_member(chat_id, user_id)
    except ChatAdminRequired:
        return "I don't have permission to unban members."
    except Exception as e:
        return f"Error: {e}"

    user_mention = mention(user_id, first_name)
    return f"{user_mention} was unbanned."


async def mute_user(chat_id, user_id, first_name, reason=None, time=None):
    try:
        if time:
            mute_end_time = datetime.datetime.now() + time
            await app.restrict_chat_member(chat_id, user_id, ChatPermissions(), mute_end_time)
        else:
            await app.restrict_chat_member(chat_id, user_id, ChatPermissions())
    except ChatAdminRequired:
        return "I don't have permission to mute members.", False
    except UserAdminInvalid:
        return "I can't mute an admin!", False
    except Exception as e:
        return f"Error: {e}", False

    user_mention = mention(user_id, first_name)
    message = f"{user_mention} was muted.\n"
    if reason:
        message += f"Reason: `{reason}`"
    if time:
        message += f"Duration: `{time}`"
    return message, True


async def unmute_user(chat_id, user_id, first_name):
    try:
        await app.restrict_chat_member(chat_id, user_id, ChatPermissions(
            can_send_messages=True,
            can_send_media_messages=True,
            can_send_other_messages=True,
            can_send_polls=True,
            can_add_web_page_previews=True,
            can_invite_users=True
        ))
    except ChatAdminRequired:
        return "I don't have permission to unmute members."
    except Exception as e:
        return f"Error: {e}"

    user_mention = mention(user_id, first_name)
    return f"{user_mention} was unmuted."


#@app.on_message(filters.command("ban") & (admin | owner), group=898989898979)
@handler("ban", gc_admin=True, dev_cmd=True)
async def ban_handler(client, message):
    chat_id = message.chat.id

    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
        first_name = message.reply_to_message.from_user.first_name
        reason = " ".join(message.command[1:]) if len(message.command) > 1 else None
    elif len(message.command) > 1:
        try:
            user_id = int(message.command[1])
            first_name = "User"
        except ValueError:
            user_data = await get_userid_from_username(message.command[1])
            if not user_data:
                return await message.reply_text("User not found.")
            user_id, first_name = user_data
        reason = " ".join(message.command[2:]) if len(message.command) > 2 else None
    else:
        return await message.reply_text("Please provide a user to ban.")

    response, success = await ban_user(chat_id, user_id, first_name, reason)
    await message.reply_text(response)


#@app.on_message(filters.command("unban") & (admin | owner), group=898989898979)
@bot("unban", gc_admin=True, dev_cmd=True)
async def unban_handler(client, message):
    chat_id = message.chat.id

    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
        first_name = message.reply_to_message.from_user.first_name
    elif len(message.command) > 1:
        try:
            user_id = int(message.command[1])
            first_name = "User"
        except ValueError:
            user_data = await get_userid_from_username(message.command[1])
            if not user_data:
                return await message.reply_text("User not found.")
            user_id, first_name = user_data
    else:
        return await message.reply_text("Please provide a user to unban.")

    response = await unban_user(chat_id, user_id, first_name)
    await message.reply_text(response)


@app.on_message(filters.command("mute") & (admin | owner), group=898989898979)
async def mute_handler(client, message):
    chat_id = message.chat.id

    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
        first_name = message.reply_to_message.from_user.first_name
        reason = " ".join(message.command[1:]) if len(message.command) > 1 else None
    elif len(message.command) > 1:
        try:
            user_id = int(message.command[1])
            first_name = "User"
        except ValueError:
            user_data = await get_userid_from_username(message.command[1])
            if not user_data:
                return await message.reply_text("User not found.")
            user_id, first_name = user_data
        reason = " ".join(message.command[2:]) if len(message.command) > 2 else None
    else:
        return await message.reply_text("Please provide a user to mute.")

    response, success = await mute_user(chat_id, user_id, first_name, reason)
    await message.reply_text(response)


@app.on_message(filters.command("unmute") & (admin | owner), group=898989898979)
async def unmute_handler(client, message):
    chat_id = message.chat.id

    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
        first_name = message.reply_to_message.from_user.first_name
    elif len(message.command) > 1:
        try:
            user_id = int(message.command[1])
            first_name = "User"
        except ValueError:
            user_data = await get_userid_from_username(message.command[1])
            if not user_data:
                return await message.reply_text("User not found.")
            user_id, first_name = user_data
    else:
        return await message.reply_text("Please provide a user to unmute.")

    response = await unmute_user(chat_id, user_id, first_name)
    await message.reply_text(response)


@app.on_message(filters.command("tmute") & (admin | owner), group=898989898979)
async def tmute_handler(client, message):
    chat_id = message.chat.id

    if len(message.command) > 2:
        try:
            time_value = int(message.command[2][:-1])
            time_unit = message.command[2][-1]
            if time_unit == "m":
                mute_duration = datetime.timedelta(minutes=time_value)
            elif time_unit == "h":
                mute_duration = datetime.timedelta(hours=time_value)
            elif time_unit == "d":
                mute_duration = datetime.timedelta(days=time_value)
            else:
                return await message.reply_text("Invalid time unit. Use `m`, `h`, or `d`.")
        except (ValueError, IndexError):
            return await message.reply_text("Invalid time format. Example: `10m`, `2h`.")

        try:
            user_id = int(message.command[1])
            first_name = "User"
        except ValueError:
            user_data = await get_userid_from_username(message.command[1])
            if not user_data:
                return await message.reply_text("User not found.")
            user_id, first_name = user_data
    elif message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
        first_name = message.reply_to_message.from_user.first_name
        mute_duration = datetime.timedelta(minutes=10)  # Default 10 minutes
    else:
        return await message.reply_text("Provide a user and mute duration.")

    response, success = await mute_user(chat_id, user_id, first_name, time=mute_duration)
    await message.reply_text(response)
