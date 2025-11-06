from pyrogram import filters
from pyrogram.errors import RPCError
from pyrogram.types import Message

from Anonymous import LOGGER
from Anonymous import app
from Anonymous.database.chats_db import Chats
from Anonymous.database.users_db import Users


@app.on_message(filters.group, group=898989898979)
async def initial_works(_, m: Message):
    try:
        chatdb = Chats(m.chat.id)
        
        # Handle chat migration
        if m.migrate_to_chat_id or m.migrate_from_chat_id:
            new_chat = m.migrate_to_chat_id or m.chat.id
            try:
                await migrate_chat(m, new_chat)
            except RPCError as ef:
                LOGGER.error(f"Migration error: {ef}")
            return

        user_to_update = None
        
        if m.reply_to_message and not m.forward_origin:
            if m.reply_to_message.from_user:
                user_to_update = m.reply_to_message.from_user
        elif m.forward_origin and m.forward_origin.sender_user:
            user_to_update = m.forward_origin.sender_user
        elif m.reply_to_message and m.reply_to_message.forward_origin and m.reply_to_message.forward_origin.sender_user:
            user_to_update = m.reply_to_message.forward_origin.sender_user
        elif m.from_user:
            user_to_update = m.from_user

        if user_to_update:
            try:
                chatdb.update_chat(m.chat.title, user_to_update.id)

                full_name = (
                    f"{user_to_update.first_name} {user_to_update.last_name}"
                    if user_to_update.last_name else user_to_update.first_name
                )
                Users(user_to_update.id).update_user(full_name, user_to_update.username)
            except Exception as e:
                LOGGER.error(f"Error updating user/chat info: {e}")

    except Exception as e:
        LOGGER.error(f"Error in initial_works: {e}")
    return


async def migrate_chat(m: Message, new_chat: int) -> None:
    try:
        LOGGER.info(f"Migrating from {m.chat.id} to {new_chat}...")
        chatdb = Chats(m.chat.id)
        userdb = Users(m.chat.id)
        chatdb.migrate_chat(new_chat)
        userdb.migrate_chat(new_chat)
        LOGGER.info(f"Successfully migrated from {m.chat.id} to {new_chat}!")
    except Exception as e:
        LOGGER.error(f"Migration failed: {e}")
        raise
