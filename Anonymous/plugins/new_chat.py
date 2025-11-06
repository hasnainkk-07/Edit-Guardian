# (©) Anonymous Emperor 

from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, ChatMemberUpdated
from pyrogram.enums import ChatType, ChatMemberStatus
from Anonymous.config import Config
from Anonymous import app
from motor.motor_asyncio import AsyncIOMotorClient

# MongoDB connection setup
client = AsyncIOMotorClient(Config.MONGO_URI)
db = client[Config.DB_NAME]
chats_collection = db["chats"]

async def add_chat(chat_id: int):
    """Add a chat ID to the database."""
    await chats_collection.update_one(
        {"chat_id": chat_id},
        {"$set": {"chat_id": chat_id}},
        upsert=True
    )

# Event for handling new chat addition
@app.on_chat_member_updated(filters.group)
async def handler(client, event: ChatMemberUpdated):
    """Log new group joins to LOG_CHANNEL_ID with Pyrogram."""
    if event.new_chat_member and event.new_chat_member.user.id == (await client.get_me()).id:
        chat = await client.get_chat(event.chat.id)
        added_by = event.from_user

        # Get member count
        member_count = await client.get_chat_members_count(chat.id)

        # Get invite link if available
        try:
            invite_link = await client.export_chat_invite_link(chat.id)
        except Exception as e:
            invite_link = "Not available"

        added_by_mention = f"<a href='tg://user?id={added_by.id}'>{added_by.first_name}</a>"

        # Compose the message
        message_text = f"""
🛡️ **Hey {added_by_mention},**
Thanks for adding me to the group [{chat.title}](https://t.me/{chat.username})! 🛡️

I'm here to make your group safer and more fun! Tap the button below to explore my features.

✨ **Main Features**:

1. **Protection Suite**:
   - Auto-delete edited messages
   - `/setdelay` - Auto-delete images after time (30s, 1h, etc)
   - Link/abuse word filters
   - `/permit` system for exceptions

2. **🎮 Toji Word Game**:
   - `/new` - Start word guessing game
   - 3-7 letter word challenges
   - Leaderboards & points system
   - `/hint` - Get letter hints

3. **Moderation Tools**:
   - Purge & ban commands
   - Temporary muting
   - Message cleaning

4. **Admin Controls**:
   - Word management
   - Broadcast messages
   - Group statistics

🚀 **Let's make this group awesome together!**  
Need help? Use /help or ask me! 💬
"""

        # Send the message to the new group
        try:
            await client.send_message(
                chat.id,
                message_text,
                disable_web_page_preview=True,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("Add Me", url="http://t.me/Toji_ProBot?startgroup=true")],
                    [InlineKeyboardButton("Support", url="https://t.me/Raiden_Support")]
                ])
            )
        except Exception as e:
            print(f"Failed to send welcome message to the group: {e}")

        # Log the new group details in the log channel
        log_message = f"""
#NEW_GROUP
┏━━━━━━━━━━━━━━━┓
➢ 𝖦𝗋𝗈𝗎𝗉 𝖭𝖺𝗆𝖾: {chat.title}
➢ 𝖦𝗋𝗈𝗎𝗉 𝖨𝖣: {chat.id}
➢ 𝖦𝗋𝗈𝗎𝗉 𝖴𝗌𝖾𝗋𝗇𝖺𝗆𝖾: @{chat.username if chat.username else 'None'}
➢ 𝖠𝖽𝖽𝖾𝖽 𝖡𝗒: {added_by_mention} [𝖨𝖣: {added_by.id}]
➢ 𝖬𝖾𝗆𝖻𝖾𝗋 𝖢𝗈𝗎𝗇𝗍: {member_count}
➢ 𝖫𝗂𝗇𝗄: {invite_link}
┗━━━━━━━━━━━━━━━┛
"""
        try:
            await client.send_message(Config.LOG_CHANNEL_ID, log_message)
        except Exception as e:
            print(f"Failed to send message to LOG_CHANNEL_ID: {e}")

async def add_chat(chat_id: int):
    """Add a chat ID to the database."""
    await chats_collection.update_one(
        {"chat_id": chat_id},
        {"$set": {"chat_id": chat_id, "timestamp": int(time.time())}},
        upsert=True
    )


@app.on_message(filters.left_chat_member)
async def handle_left_chat_member(client: Client, message: Message):
    """Handle bot being removed from a group."""
    try:
        if message.left_chat_member and message.left_chat_member.id == (await client.get_me()).id:
            chat = message.chat
            remover = message.from_user
            remover_mention = f"<a href='tg://user?id={remover.id}'>{remover.first_name}</a>" if remover else "Unknown"

            log_text = f"""
#LEFT_GROUP
🚪 Bot was removed from a group!

➤ Group Name: {chat.title}
➤ Group ID: `{chat.id}`
➤ Username: @{chat.username if chat.username else 'None'}
➤ Removed By: {remover_mention}
➤ Timestamp: {int(time.time())}
"""
            try:
                await client.send_message(Config.LOG_CHANNEL_ID, log_text)
            except Exception as e:
                print(f"Failed to log bot leave: {e}")

    except Exception as e:
        print(f"Error in handle_left_chat_member: {e}")
cept Exception as e:
        print(f"Error in handle_left_chat_member: {e}")
