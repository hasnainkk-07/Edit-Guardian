# (©) Anonymous Emperor 

from pyrogram.filters import create
from pyrogram.enums import ChatMemberStatus as CMSG, ChatType
from pyrogram.types import Message, CallbackQuery
from Anonymous.config import Config
from Anonymous.helpers.caching import ADMIN_CACHE, admin_cache_reload

DEV_USERS = Config.OWNER_ID

async def admin_check_func(_, __, m: Message or CallbackQuery):
    """Check if user is Admin or not."""
    if isinstance(m, CallbackQuery):
        m = m.message

    if m.chat.type not in [ChatType.SUPERGROUP, ChatType.GROUP]:
        return False

    # Telegram and GroupAnonymousBot
    if m.sender_chat:
        return True

    if not m.from_user:
        return False

    try:
        admin_group = {i[0] for i in ADMIN_CACHE[m.chat.id]}
    except KeyError:
        admin_group = {
            i[0] for i in await admin_cache_reload(m, "custom_filter_update")
        }
    except ValueError as ef:
        # To make language selection work in private chat of user, i.e. PM
        if ("The chat_id" and "belongs to a user") in ef:
            return True

    if m.from_user.id in admin_group:
        return True

    await m.reply_text(text="You cannot use an admin command!")
    return False

async def bot_owner_check_func(_, __, m: Message or CallbackQuery):
    """Check if the user is the bot owner."""
    if isinstance(m, CallbackQuery):
        m = m.message

    # Check if the chat is a group or supergroup
    if m.chat.type not in [ChatType.SUPERGROUP, ChatType.GROUP]:
        return False

    if not m.from_user:
        return False

    # Check if the user is in the list of bot owners
    if m.from_user.id in Config.OWNER_ID:
        return True

    return False

async def owner_check_func(_, __, m: Message or CallbackQuery):
    """Check if user is Owner or not."""
    if isinstance(m, CallbackQuery):
        m = m.message

    if m.chat.type not in [ChatType.SUPERGROUP, ChatType.GROUP]:
        return False

    if not m.from_user:
        return False

    user = await m.chat.get_member(m.from_user.id)

    if user.status == CMSG.OWNER:
        status = True
    else:
        status = False
        # Ignore message if the user is the bot owner or in DEV_USERS
        if m.from_user.id not in DEV_USERS and m.from_user.id not in Config.OWNER_ID:
            if user.status == CMSG.ADMINISTRATOR:
                msg = "You're an admin only, stay in your limits!"
            else:
                msg = "Do you think that you can execute owner commands?"
            await m.reply_text(msg)

    return status


# Filters
admin_filter = create(admin_check_func)
bot_owner_filter = create(bot_owner_check_func)
owner = create(bot_owner_check_func)
owner_filter = create(owner_check_func)
