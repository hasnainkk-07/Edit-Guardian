# (©) Anonymous Emperor 

import asyncio
from pyrogram import filters
from Anonymous import app as pbot
from Anonymous.bot import handler
from Anonymous.database.chats_db import Chats
from Anonymous.database.users_db import Users
from Anonymous.config import Config

OWNER_ID = Config.OWNER_ID

chat_db = Chats
user_db = Users

#@pbot.on_message(filters.command("broadcast") & filters.user(OWNER_ID), group=898989898979)
@handler("broadcast", dev_cmd=True)
async def broadcast_post(_, message):
    if message.reply_to_message:
        to_send = message.reply_to_message.id
    else:
        return await message.reply_text("Reply to some post to broadcast.")

    # Broadcasting to chats
    chat_list = chat_db.list_chats_by_id()
    failed_chats = 0
    for chat_id in chat_list:
        try:
            await pbot.forward_messages(chat_id=chat_id, from_chat_id=message.chat.id, message_ids=to_send)
            await asyncio.sleep(1)
        except Exception:
            failed_chats += 1

    # Broadcasting to users
    user_list = user_db.list_users_by_id()
    failed_users = 0
    for user_id in user_list:
        try:
            await pbot.forward_messages(chat_id=user_id, from_chat_id=message.chat.id, message_ids=to_send)
            await asyncio.sleep(1)
        except Exception:
            failed_users += 1

    # Sending report to owner
    await pbot.send_message(
        OWNER_ID[0],  # Assuming the first OWNER_ID is the main owner
        text=(
            f"Broadcast complete.\n\n"
            f"Failed to send to:\n"
            f"• Chats: <code>{failed_chats}</code>\n"
            f"• Users: <code>{failed_users}</code>\n\n"
            "Check logs for more details."
        ),
        parse_mode="html"
      )
