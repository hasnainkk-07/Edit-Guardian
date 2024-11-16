from pyrogram import Client, filters
from pyrogram.types import Message
from pymongo import MongoClient

# Client Need Api'ss and Token
api_id = 12380656
api_hash = "d927c13beaaf5110f25c505b7c071273"
bot_token = "7391930298:AAEGSbfUFsFErfue_zamTTYhDYOhZAbxuBM"

# MongoDB setup
mongo = MongoClient("mongodb+srv://bikash:bikash@bikash.3jkvhp7.mongodb.net/?retryWrites=true&w=majority")  # Replace with your MongoDB URI
db = mongo["EditDeleterBot"]

# Collections
approved_users = db["approved_users"]
gban_collection = db["gban_users"]

# Bot credentials
app = Client(
    "EditDeleterBot",
    api_id=api_id,
    api_hash=api_hash,
    bot_token=bot_token,
)

OWNER_ID = 6346273488  # Replace with your Telegram user ID

# Admin check function
async def is_admin(client, message: Message):
    chat_member = await client.get_chat_member(message.chat.id, message.from_user.id)
    return chat_member.status in ["administrator", "creator"]

@app.on_message(filters.command("start"))
async def start(client, message: Message):
    await message.reply_text("Hello! I'm here to manage edited messages. Use /help for details.")

@app.on_message(filters.command("help"))
async def help(client, message: Message):
    await message.reply_text(
        "Commands:\n"
        "/start - Check my availability\n"
        "/help - Get information about me\n"
        "/approve - Approve a user (Admin only)\n"
        "/unapprove - Unapprove a user (Admin only)\n"
        "/approved - View approved users list\n"
        "/gban - Globally ban a user (Owner only)\n"
        "/ungban - Globally unban a user (Owner only)\n"
        "/checkban - Check if a user is globally banned\n"
        "Feature: Automatically deletes edited messages unless the user is approved."
    )

@app.on_message(filters.command("approve"))
async def approve_user(client, message: Message):
    if not await is_admin(client, message):
        return await message.reply_text("You must be an admin to use this command.")
    if not message.reply_to_message:
        return await message.reply_text("Reply to the user you want to approve.")
    
    user_id = message.reply_to_message.from_user.id
    chat_id = message.chat.id

    approved_users.insert_one({"chat_id": chat_id, "user_id": user_id})
    await message.reply_text(f"User {user_id} has been approved.")

@app.on_message(filters.command("unapprove"))
async def unapprove_user(client, message: Message):
    if not await is_admin(client, message):
        return await message.reply_text("You must be an admin to use this command.")
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
    user_list = "\n".join([str(user["user_id"]) for user in users])
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

@app.on_edited_message(filters.group)
async def delete_edited_message(client, message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    if not approved_users.find_one({"chat_id": chat_id, "user_id": user_id}):
        await message.delete()

app.run()
