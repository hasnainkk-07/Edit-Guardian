from pyrogram import Client, filters
from pyrogram.types import Message
from pymongo import MongoClient
from admins import admin_filter  # Assuming you've imported admin_filter from an 'admins' module
import html

# MongoDB setup
mongo = MongoClient("mongodb+srv://bikash:bikash@bikash.3jkvhp7.mongodb.net/?retryWrites=true&w=majority")  # Replace with your MongoDB URI
db = mongo["hasnainkk"]

# Collections
approved_users = db["approved_users"]
gban_collection = db["gban_users"]

# Bot credentials
api_id = 12380656
api_hash = "d927c13beaaf5110f25c505b7c071273"
bot_token = "7391930298:AAEGSbfUFsFErfue_zamTTYhDYOhZAbxuBM"

app = Client(
    "hasnainkk",
    api_id=api_id,
    api_hash=api_hash,
    bot_token=bot_token,
)

OWNER_ID = 6346273488  # Replace with your Telegram user ID
SUDO_USERS = [1805959544, 1284920298, 5907205317, 5881613383]  # Sudo users list

# Admin check function (to be used in the filter)
async def is_admin(client, message: Message):
    chat_member = await client.get_chat_member(message.chat.id, message.from_user.id)
    return chat_member.status in ["administrator", "creator"]

@app.on_message(filters.command("approve") & admin_filter)
async def approve_user(client, message: Message):
    if not message.reply_to_message:
        return await message.reply_text("Reply to the user you want to approve.")
    
    user_id = message.reply_to_message.from_user.id
    chat_id = message.chat.id
    first_name = message.reply_to_message.from_user.first_name

    approved_users.insert_one({"chat_id": chat_id, "user_id": user_id})
    
    user_mention = f"<a href='tg://user?id={user_id}'>{html.escape(first_name)}</a>"
    await message.reply_text(f"User {user_mention} has been approved.")

@app.on_message(filters.command("unapprove") & admin_filter)
async def unapprove_user(client, message: Message):
    if not message.reply_to_message:
        return await message.reply_text("Reply to the user you want to unapprove.")
    
    user_id = message.reply_to_message.from_user.id
    chat_id = message.chat.id
    first_name = message.reply_to_message.from_user.first_name

    approved_users.delete_one({"chat_id": chat_id, "user_id": user_id})
    
    user_mention = f"<a href='tg://user?id={user_id}'>{html.escape(first_name)}</a>"
    await message.reply_text(f"User {user_mention} has been unapproved.")

@app.on_message(filters.command("approved"))
async def list_approved_users(client, message: Message):
    chat_id = message.chat.id
    users = approved_users.find({"chat_id": chat_id})
    if users:
        user_list = "\n".join([f"<a href='tg://user?id={user['user_id']}'>{html.escape(client.get_users(user['user_id']).first_name)}</a>" for user in users])
        await message.reply_text(f"Approved Users:\n{user_list}", parse_mode="HTML")
    else:
        await message.reply_text("No approved users.")

@app.on_message(filters.command("sudolist") & filters.user(OWNER_ID))
async def sudo_list(client, message: Message):
    sudo_list_str = ""
    for user_id in SUDO_USERS:
        try:
            user = await client.get_users(user_id)
            first_name = user.first_name
            user_mention = f"<a href='tg://user?id={user_id}'>{html.escape(first_name)}</a>"
            sudo_list_str += f"{user_mention}\n"
        except Exception as e:
            continue
    if sudo_list_str:
        await message.reply_text(f"Sudo Users List:\n{sudo_list_str}", parse_mode="HTML")
    else:
        await message.reply_text("No sudo users.")

@app.on_message(filters.command("stats") & filters.user(OWNER_ID))
async def stats(client, message: Message):
    # Example stats: number of users and chats the bot is in
    user_count = db.users.count_documents({})
    chat_count = db.chats.count_documents({})
    await message.reply_text(f"Stats:\nUsers: {user_count}\nChats: {chat_count}")

@app.on_edited_message(filters.group)
async def delete_edited_message(client, message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    if user_id in SUDO_USERS or user_id == OWNER_ID or approved_users.find_one({"chat_id": chat_id, "user_id": user_id}):
        # Don't delete message if it's from owner, sudo users, or approved users
        return

    user_mention = f"<a href='tg://user?id={user_id}'>{html.escape(message.from_user.first_name)}</a>"
    await message.reply_text(f"{user_mention} just edited a message. I deleted their message.", parse_mode="HTML")
    await message.delete()

app.run()
