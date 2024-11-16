import html
from pyrogram import Client, filters
from pyrogram.types import Message
from pymongo import MongoClient
from admins import admin_filter  # Assuming you've imported admin_filter from an 'admins' module

# MongoDB setup
mongo = MongoClient("mongodb+srv://bikash:bikash@bikash.3jkvhp7.mongodb.net/?retryWrites=true&w=majority")  # Replace with your MongoDB URI
db = mongo["EditDeleterBot"]

# Collections
approved_users = db["approved_users"]
gban_collection = db["gban_users"]

# Bot credentials
api_id = 12380656
api_hash = "d927c13beaaf5110f25c505b7c071273"
bot_token = "7391930298:AAEGSbfUFsFErfue_zamTTYhDYOhZAbxuBM"

app = Client(
    "EditDeleterBot",
    api_id=api_id,
    api_hash=api_hash,
    bot_token=bot_token,
)

OWNER_ID = 6346273488  # Replace with your Telegram user ID
SUDO_USERS = [1805959544, 1284920298, 5907205317, 5881613383]  # Sudo users list


# Function to create a mention for a user
def create_mention(user_id, first_name):
    return f"<a href='tg://user?id={user_id}'>{html.escape(first_name)}</a>"


mention = create_mention(user_id, message.from_user.first_name)

# Admin check function (to be used in the filter)
async def is_admin(client, message: Message):
    chat_member = await client.get_chat_member(message.chat.id, message.from_user.id)
    return chat_member.status in ["administrator", "creator"]

@app.on_message(filters.command("start"))
async def start(client, message: Message):
    # Mention user by first name
    user_first_name = message.from_user.first_name
    await message.reply_text(f"Hello, {mention} ! Welcome to the Edit Deleter Bot. Use /help for commands.")

@app.on_message(filters.command("help"))
async def help(client, message: Message):
    # Provide help information
    help_text = (
        "This bot helps you with approving/unapproving users and global banning.\n"
        "Here are the available commands:\n\n"
        "/start - Start message\n"
        "/help - Get help information\n"
        "/approve - Approve a user (reply to their message)\n"
        "/unapprove - Unapprove a user (reply to their message)\n"
        "/approved - List approved users\n"
        "/gban <user_id> <reason> - Globally ban a user\n"
        "/ungban <user_id> - Unban a globally banned user\n"
        "/checkban <user_id> - Check if a user is globally banned\n"
        "/addsudo <user_id> - Add a user to sudo list\n"
        "/sudolist - List all sudo users\n"
        "/stats - Get bot stats"
    )
    await message.reply_text(help_text)

@app.on_message(filters.command("approve") & admin_filter)
async def approve_user(client, message: Message):
    if not message.reply_to_message:
        return await message.reply_text("Reply to the user you want to approve.")
    
    user_id = message.reply_to_message.from_user.id
    first_name = message.reply_to_message.from_user.first_name  # Store first name
    chat_id = message.chat.id

    approved_users.insert_one({"chat_id": chat_id, "user_id": user_id, "first_name": first_name})
    await message.reply_text(f"User {first_name} has been approved.")

@app.on_message(filters.command("unapprove") & admin_filter)
async def unapprove_user(client, message: Message):
    if not message.reply_to_message:
        return await message.reply_text("Reply to the user you want to unapprove.")
    
    user_id = message.reply_to_message.from_user.id
    chat_id = message.chat.id

    approved_users.delete_one({"chat_id": chat_id, "user_id": user_id})
    await message.reply_text(f"User {user_id} has been unapproved.")

@app.on_message(filters.command("approved"))
async def list_approved_users(client, message: Message):
    chat_id = message.chat.id
    users = approved_users.find({"chat_id": chat_id})
    user_list = "\n".join([f"{user['first_name']} ({user['user_id']})" for user in users])
    await message.reply_text(f"Approved Users:\n{user_list if user_list else 'No approved users.'}")

@app.on_message(filters.command("gban") & filters.user(OWNER_ID))
async def gban_user(client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("Usage: /gban <user_id> <reason>")
    
    args = message.command[1:]
    user_id = int(args[0])
    reason = " ".join(args[1:]) if len(args) > 1 else "No reason provided"

    gban_collection.insert_one({"user_id": user_id, "reason": reason})

    async for dialog in client.iter_dialogs():
        if dialog.chat.type in ["group", "supergroup"]:
            try:
                await client.kick_chat_member(dialog.chat.id, user_id)
            except Exception:
                continue

    await message.reply_text(f"User {user_id} has been globally banned.\nReason: {reason}")

@app.on_message(filters.command("ungban") & filters.user(OWNER_ID))
async def ungban_user(client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("Usage: /ungban <user_id>")
    
    user_id = int(message.command[1])

    gban_collection.delete_one({"user_id": user_id})
    await message.reply_text(f"User {user_id} has been globally unbanned.")

@app.on_message(filters.command("checkban"))
async def check_ban(client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("Usage: /checkban <user_id>")
    
    user_id = int(message.command[1])
    ban_info = gban_collection.find_one({"user_id": user_id})

    if ban_info:
        await message.reply_text(f"User {user_id} is globally banned.\nReason: {ban_info['reason']}")
    else:
        await message.reply_text(f"User {user_id} is not globally banned.")

@app.on_message(filters.command("addsudo") & filters.user(OWNER_ID))
async def add_sudo_user(client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("Usage: /addsudo <user_id>")
    
    user_id = int(message.command[1])
    if user_id not in SUDO_USERS:
        SUDO_USERS.append(user_id)
        await message.reply_text(f"User {user_id} has been added to the sudo list.")
    else:
        await message.reply_text(f"User {user_id} is already in the sudo list.")

@app.on_message(filters.command("sudolist") & filters.user(OWNER_ID))
async def sudo_list(client, message: Message):
    sudo_list_str = "\n".join(str(user_id) for user_id in SUDO_USERS)
    await message.reply_text(f"Sudo Users List:\n{sudo_list_str if sudo_list_str else 'No sudo users.'}")

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

    # Use the mention function
    mention = create_mention(user_id, message.from_user.first_name)

    if user_id in SUDO_USERS or user_id == OWNER_ID or approved_users.find_one({"chat_id": chat_id, "user_id": user_id}):
        # Don't delete the message if it's from owner, sudo users, or approved users
        return
    
    # Delete the edited message
    await message.delete()
    
    # Send a reply with the user's first name and user ID
    await message.reply_text(f"{mention} (ID: {user_id}) just edited a message. I deleted their message.", parse_mode="html")


app.run()
