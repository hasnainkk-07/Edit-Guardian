from pyrogram import Client, filters
from pymongo import MongoClient
from pyrogram.types import Message
from admins import admin_filter
import html
import asyncio

# MongoDB setup
mongo = MongoClient("mongodb+srv://bikash:bikash@bikash.3jkvhp7.mongodb.net/?retryWrites=true&w=majority")
db = mongo["BotDB"]

# Collections
users_collection = db["users"]
chats_collection = db["chats"]
approved_users = db["approved_users"]
gban_collection = db["gban_users"]
sudo_users_collection = db["sudo_users"]

# Bot credentials
api_id = 12380656
api_hash = "d927c13beaaf5110f25c505b7c071273"
bot_token = "7391930298:AAEGSbfUFsFErfue_zamTTYhDYOhZAbxuBM"

app = Client("Bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

OWNER_ID = 6346273488  # Replace with your Telegram user ID
SUDO_USERS = [1805959544, 1284920298, 5907205317, 5881613383]  # Sudo users list

# Track new chats (when the bot is added to a new chat)
@app.on_chat_member_updated(filters.new_chat_members)
async def track_new_chat(client, message: Message):
    if message.chat.id not in chats_collection.distinct("chat_id"):
        chats_collection.insert_one({"chat_id": message.chat.id})

# Track unique users (when the bot receives a message)
@app.on_message(filters.text)
async def track_user(client, message: Message):
    if message.from_user:
        user_id = message.from_user.id
        if not users_collection.find_one({"user_id": user_id}):
            users_collection.insert_one({"user_id": user_id})

# Stats Command (Showing Bot Statistics)
@app.on_message(filters.command("stats") & filters.user(OWNER_ID))
async def stats(client, message: Message):
    approved_count = approved_users.count_documents({})
    gban_count = gban_collection.count_documents({})
    sudo_count = sudo_users_collection.count_documents({})
    user_count = users_collection.count_documents({})
    chat_count = chats_collection.count_documents({})
    
    stats_text = f"""
    Bot Statistics:
    Approved Users: {approved_count}
    Globally Banned Users: {gban_count}
    Sudo Users: {sudo_count}
    Unique Users: {user_count}
    Total Chats: {chat_count}
    """
    
    await message.reply_text(stats_text)

# Start Command (Welcoming the User)
@app.on_message(filters.command("start"))
async def start(client, message: Message):
    user_mention = f"<a href='tg://user?id={message.from_user.id}'>{html.escape(message.from_user.first_name)}</a>"
    await message.reply_text(f"Hello {user_mention}, Welcome to the bot! Use /help to get the list of commands.", parse_mode="HTML")

# Help Command (Showing Available Commands)
@app.on_message(filters.command("help"))
async def help(client, message: Message):
    help_text = """
    Available Commands:
    /approve - Approve a user
    /unapprove - Unapprove a user
    /gban - Global ban a user
    /ungban - Unban a user from global ban
    /checkban - Check if a user is globally banned
    /addsudo - Add a user to sudo list
    /removesudo - Remove a user from sudo list
    /sudolist - List all sudo users
    /stats - Get bot statistics
    /clonebot - Clone bot with new token (owner only)
    /start - Start the bot
    """
    await message.reply_text(help_text)

# Add Sudo User Command
@app.on_message(filters.command("addsudo") & filters.user(OWNER_ID))
async def add_sudo_user(client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("Usage: /addsudo <user_id>")
    
    user_id = int(message.command[1])
    
    if sudo_users_collection.find_one({"user_id": user_id}):
        return await message.reply_text(f"User {user_id} is already in the sudo list.")
    
    sudo_users_collection.insert_one({"user_id": user_id})
    SUDO_USERS.append(user_id)
    await message.reply_text(f"User {user_id} has been added to the sudo list.")

# Remove Sudo User Command
@app.on_message(filters.command("removesudo") & filters.user(OWNER_ID))
async def remove_sudo_user(client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("Usage: /removesudo <user_id>")
    
    user_id = int(message.command[1])
    
    if not sudo_users_collection.find_one({"user_id": user_id}):
        return await message.reply_text(f"User {user_id} is not in the sudo list.")
    
    sudo_users_collection.delete_one({"user_id": user_id})
    SUDO_USERS.remove(user_id)
    await message.reply_text(f"User {user_id} has been removed from the sudo list.")

# Sudo List Command
@app.on_message(filters.command("sudolist") & filters.user(OWNER_ID))
async def sudolist(client, message: Message):
    sudo_users = sudo_users_collection.find()
    sudo_list_text = "Sudo Users List:\n"
    for user in sudo_users:
        sudo_list_text += f"- {user['user_id']}\n"
    
    await message.reply_text(sudo_list_text)

# Approve User Command
@app.on_message(filters.command("approve") & filters.user(OWNER_ID))
async def approve_user(client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("Usage: /approve <user_id>")
    
    user_id = int(message.command[1])
    
    if approved_users.find_one({"user_id": user_id}):
        return await message.reply_text(f"User {user_id} is already approved.")
    
    approved_users.insert_one({"user_id": user_id})
    await message.reply_text(f"User {user_id} has been approved.")

# Unapprove User Command
@app.on_message(filters.command("unapprove") & filters.user(OWNER_ID))
async def unapprove_user(client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("Usage: /unapprove <user_id>")
    
    user_id = int(message.command[1])
    
    if not approved_users.find_one({"user_id": user_id}):
        return await message.reply_text(f"User {user_id} is not approved.")
    
    approved_users.delete_one({"user_id": user_id})
    await message.reply_text(f"User {user_id} has been unapproved.")

# Global Ban User Command
@app.on_message(filters.command("gban") & filters.user(OWNER_ID))
async def gban_user(client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("Usage: /gban <user_id>")
    
    user_id = int(message.command[1])
    
    if gban_collection.find_one({"user_id": user_id}):
        return await message.reply_text(f"User {user_id} is already globally banned.")
    
    gban_collection.insert_one({"user_id": user_id})
    await message.reply_text(f"User {user_id} has been globally banned.")

# Unban Global Ban User Command
@app.on_message(filters.command("ungban") & filters.user(OWNER_ID))
async def ungban_user(client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("Usage: /ungban <user_id>")
    
    user_id = int(message.command[1])
    
    if not gban_collection.find_one({"user_id": user_id}):
        return await message.reply_text(f"User {user_id} is not globally banned.")
    
    gban_collection.delete_one({"user_id": user_id})
    await message.reply_text(f"User {user_id} has been unbanned.")

# Check if User is Globally Banned
@app.on_message(filters.command("checkban") & filters.user(OWNER_ID))
async def checkban_user(client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("Usage: /checkban <user_id>")
    
    user_id = int(message.command[1])
    
    if gban_collection.find_one({"user_id": user_id}):
        return await message.reply_text(f"User {user_id} is globally banned.")
    
    await message.reply_text(f"User {user_id} is not globally banned.")

# Clone Bot Command (for bot cloning)
@app.on_message(filters.command("clonebot") & filters.user(OWNER_ID))
async def clone_bot(client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("Usage: /clonebot <new_bot_token>")
    
    new_token = message.command[1]
    
    try:
        # Creating a new Client with the new token
        clone_bot = Client("ClonedBot", api_id=api_id, api_hash=api_hash, bot_token=new_token)
        
        # Start the cloned bot in the background
        asyncio.create_task(clone_bot.start())
        await message.reply_text(f"Cloned bot started successfully with token: {new_token}")
    except Exception as e:
    #    await message.reply_text(f"Failed to clone the bot.
        await message.reply_text(f"Failed to clone the bot. Error: {e}")

# Shutdown Command (For stopping the bot)
@app.on_message(filters.command("shutdown") & filters.user(OWNER_ID))
async def shutdown(client, message: Message):
    await message.reply_text("Shutting down the bot...")
    await app.stop()

# Run the bot
if __name__ == "__main__":
    app.run()
