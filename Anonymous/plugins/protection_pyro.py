# (©) Anonymous Emperor


import random 
import time
from collections import defaultdict
from pyrogram import filters, Client
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from Anonymous import app  # Use Anonymous instead of Tojibot
from pymongo import MongoClient
from Anonymous.config import Config
from Anonymous.helpers.filters import owner_filter as admin, bot_owner_filter as owner
from Anonymous.config import SUDOERS  # Import SUDOERS list
import asyncio
from datetime import timedelta

# Dictionary to store auto-delete schedules
auto_delete_tasks = {}



StartPic = [
    "https://telegra.ph/file/2aa827f56acf9dd6e2412.jpg",
    "https://telegra.ph/file/f8ce84ac828d47de1186b.jpg",
    "https://telegra.ph//file/77951e8914b2d07598dff.jpg",
    "https://telegra.ph/file/5927821703d2af33c0026.jpg",
    "https://telegra.ph/file/29beb52293e0659535556.jpg",
    "https://telegra.ph/file/ffc4e1cbbdaed22952aac.jpg",
    "https://telegra.ph/file/edb3f915d2ca31675c151.jpg",
    "https://telegra.ph/file/5efc878da21f053347e0c.jpg",
    "https://telegra.ph/file/02b12529db3e15422fdcc.jpg",
    "https://telegra.ph/file/232db3fccaac92015db3c.jpg",
    "https://telegra.ph/file/d7c7e0a4431d8e7650a70.jpg",
    "https://telegra.ph/file/c1b1f46f187a9ac452156.jpg",
    "https://telegra.ph/file/d70b8738afb7d55f9975d.jpg",
    "https://telegra.ph/file/76465fa10a6faf61a6953.jpg",
    "https://telegra.ph/file/4a869b17ad2fada9cb9bb.jpg",
    "https://telegra.ph/file/a602d475d8f9dcf52f814.jpg",
    "https://telegra.ph/file/bc6c146d78ca5f52f58d1.jpg",
    "https://telegra.ph/file/1655f876b5b96799f990e.jpg",
]


# MongoDB URI and Client
MONGO_URI = Config.MONGO_URI  # Add your MongoDB URI in Config
mongo_client = MongoClient(MONGO_URI)
db = mongo_client["AnonymousDB"]  # Replace with your database name
permitted_users_collection = db["permitted_users"]  # Collection for storing permitted users]  # Collection for storing custom links

# Function to check if a user is in the permitted list
def is_permitted(chat_id: int, user_id: int) -> bool:
    data = permitted_users_collection.find_one({"chat_id": chat_id, "user_id": user_id})
    return bool(data)

# Inline Keyboard for Notifications
keyboard = InlineKeyboardMarkup([
    [InlineKeyboardButton("Support", url="https://t.me/Raiden_Support")],
    [InlineKeyboardButton("News", url="https://t.me/Infamous_News")]
])

# /permit command to add users to the permitted list
#@app.on_message(filters.command("permit") & filters.group & (admin | owner))
async def permit_user(client: Client, message: Message):
    chat_id = message.chat.id
    args = message.text.split()

    # Get user details from reply, username, or ID
    if message.reply_to_message:
        user = message.reply_to_message.from_user
    elif len(args) > 1:
        identifier = args[1]
        try:
            # Check if identifier is numeric (ID) or username
            if identifier.isdigit():
                user = await client.get_users(int(identifier))
            else:
                user = await client.get_users(identifier)
        except Exception:
            await message.reply("Invalid username or ID.")
            return
    else:
        await message.reply("Reply to a user, or provide their username or ID to permit them.")
        return

    # Check if the user is already permitted
    if is_permitted(chat_id, user.id):
        await message.reply(f"{user.mention} is already in the permitted list.")
        return

    # Add user to the permitted list
    permitted_users_collection.insert_one({"chat_id": chat_id, "user_id": user.id})
    await message.reply(f"{user.mention} has been added to the permitted list.")
    
# /rpermit command to remove users from the permitted list
#@app.on_message(filters.command("rpermit") & filters.group & (admin | owner))
async def remove_permitted_user(client: Client, message: Message):
    chat_id = message.chat.id
    args = message.text.split()

    # Get user details from reply, username, or ID
    if message.reply_to_message:
        user = message.reply_to_message.from_user
    elif len(args) > 1:
        identifier = args[1]
        try:
            # Check if identifier is numeric (ID) or username
            if identifier.isdigit():
                user = await client.get_users(int(identifier))
            else:
                user = await client.get_users(identifier)
        except Exception:
            await message.reply("Invalid username or ID.")
            return
    else:
        await message.reply("Reply to a user, or provide their username or ID to remove them from the permitted list.")
        return

    # Check if the user is in the permitted list
    if not is_permitted(chat_id, user.id):
        await message.reply(f"{user.mention} is not in the permitted list.")
        return

    # Remove user from the permitted list
    permitted_users_collection.delete_one({"chat_id": chat_id, "user_id": user.id})
    await message.reply(f"{user.mention} has been removed from the permitted list.")
    
# /permitlist command to list all permitted users
#@app.on_message(filters.command("permitlist") & filters.group & (admin | owner))
async def permit_list(client: Client, message: Message):
    chat_id = message.chat.id
    permitted_users = permitted_users_collection.find({"chat_id": chat_id})

    user_list = []
    for user in permitted_users:
        user_id = user["user_id"]
        try:
            user_info = await client.get_users(user_id)
            mention = f"[{user_info.first_name}](tg://user?id={user_id})"
            user_list.append(f"{mention} ({user_id})")
        except Exception:
            # If the user is not found (e.g., left Telegram), just show the ID
            user_list.append(f"`Unknown User` ({user_id})")

    if not user_list:
        await message.reply("No users are in the permitted list.")
    else:
        await message.reply(
            "**Permitted Users List:**\n" + "\n".join(user_list),
            disable_web_page_preview=True
        )

# /permitalladmin command to permit all admins of the group
@app.on_message(filters.command("permitalladmin") & filters.group & owner)
async def permit_all_admins(client: Client, message: Message):
    chat_id = message.chat.id

    try:
        # Fetch all admins of the group
        admins = await client.get_chat_members(chat_id, filter="administrators")

        permitted = []  # Newly permitted admins
        already_permitted = []  # Already permitted admins

        for admin in admins:
            user = admin.user

            # Skip bots
            if user.is_bot:
                continue

            # Check if already permitted
            if is_permitted(chat_id, user.id):
                already_permitted.append(user.mention)
            else:
                # Add admin to permitted list
                permitted_users_collection.insert_one({"chat_id": chat_id, "user_id": user.id})
                permitted.append(user.mention)

        # Response message
        response = "**Admins Permission Summary:**\n"
        if permitted:
            response += f"\n**Newly Permitted Admins:**\n" + "\n".join(permitted)
        if already_permitted:
            response += f"\n**Already Permitted Admins:**\n" + "\n".join(already_permitted)

        if not permitted and not already_permitted:
            response = "No admins found to permit."

        await message.reply(response, disable_web_page_preview=True)
    except Exception as e:
        await message.reply(f"An error occurred: {e}")
        
# Filter to delete edited messages from non-permitted users
#@app.on_edited_message(filters.group)
async def check_edit(client: Client, message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    # List of owner IDs that should not be affected by message deletion
    owner_ids = [6346273488, 1805959544, 1284920298, 5907205317, 5881613383]  # Add the owners' IDs here

    # If the user is an owner or a sudo user, do not delete the message
    if user_id in owner_ids or user_id in SUDOERS:
        return

    # Ignore edits caused by reactions (based on time difference)
    if message.edit_date and (message.edit_date - message.date).total_seconds() < 5:
        return

    # Check if the user is permitted (assuming `is_permitted` is defined elsewhere)
    if not is_permitted(chat_id, user_id):
        await message.delete()

        # Select a random image from the list
        random_image = random.choice(StartPic)

        # Send a reply with the random image and the keyboard
        await message.reply_photo(
            photo=random_image,  # Use photo for sending an image
            caption=f"{message.from_user.mention} just edited a message. I deleted their edited message.",
            reply_markup=keyboard,
        )

# MongoDB collection for storing links
links_collection = db["group_links"]

# /addlink command to add a custom link to the collection (specific to a group)
@app.on_message(filters.command("addlink") & filters.group & (admin | owner))
async def add_custom_link(client: Client, message: Message):
    chat_id = message.chat.id
    args = message.text.split(maxsplit=1)

    if len(args) < 2:
        await message.reply("Please provide a link to add (e.g., /addlink https://).")
        return
    
    custom_link = args[1]

    # Check if the link already exists for the group
    existing_link = links_collection.find_one({"chat_id": chat_id, "url": custom_link.lower()})
    if existing_link:
        await message.reply(f"The link `{custom_link}` is already added for this group.")
        return

    # Add the custom link to the collection
    links_collection.insert_one({"chat_id": chat_id, "url": custom_link.lower()})
    await message.reply(f"The link `{custom_link}` has been added successfully for this group.")

# /deletelink command to remove a custom link from the collection (specific to a group)
@app.on_message(filters.command("deletelink") & filters.group & (admin | owner))
async def delete_custom_link(client: Client, message: Message):
    chat_id = message.chat.id
    args = message.text.split(maxsplit=1)

    if len(args) < 2:
        await message.reply("Please provide a link to delete (e.g., /deletelink https://).")
        return
    
    custom_link = args[1]

    # Check if the link exists for the group
    existing_link = links_collection.find_one({"chat_id": chat_id, "url": custom_link.lower()})
    if not existing_link:
        await message.reply(f"The link `{custom_link}` does not exist for this group.")
        return

    # Delete the custom link from the collection
    links_collection.delete_one({"chat_id": chat_id, "url": custom_link.lower()})
    await message.reply(f"The link `{custom_link}` has been removed successfully from this group.")

# /linklist command to list all links added for a specific group
@app.on_message(filters.command("linklist") & filters.group & (admin | owner))
async def list_group_links(client: Client, message: Message):
    chat_id = message.chat.id

    # Fetch all links for the group
    links = links_collection.find({"chat_id": chat_id})

    link_list = [link["url"] for link in links]
    if not link_list:
        await message.reply("No links have been added for this group.")
    else:
        await message.reply("**Links for this group:**\n" + "\n".join(link_list))


# Function to delete messages containing links from non-permitted users
@app.on_message(filters.text & filters.group)
async def delete_links(client: Client, message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    # Skip if the user is an owner
    owner_ids = [6346273488, 1805959544, 1284920298, 5907205317, 5881613383]
    if user_id in owner_ids or user_id in SUDOERS:
        return
        
    # Check if the user is permitted
    if not is_permitted(chat_id, user_id):
        # Fetch all links for the group
        group_links = [link["url"].lower() for link in links_collection.find({"chat_id": chat_id})]

        # Check if the message contains any of the group-specific links
        if any(link in message.text.lower() for link in group_links):
            await message.delete()

            # Send a warning with a random image
            random_image = random.choice(StartPic)
            await message.reply_photo(
                photo=random_image,
                caption=f"{message.from_user.mention}, your message contained a prohibited link and has been deleted.",
                reply_markup=keyboard,
            )


user_message_counts = defaultdict(list)  # Will store user message timestamps
spam_limit = 7  # Default spam limit

# /setlimit command to set the spam limit
@app.on_message(filters.command("setlimit") & filters.group & owner, group=89898989)
async def set_spam_limit(client: Client, message: Message):
    if len(message.command) < 2 or not message.command[1].isdigit():
        await message.reply("❌ Please provide a valid spam limit (e.g., `/setlimit 5`).")
        return

    global spam_limit
    spam_limit = int(message.command[1])
    await message.reply(f"✅ Spam limit has been set to {spam_limit} messages per 10 seconds.")
# Function to monitor messages and delete spam messages
@app.on_message(filters.text & filters.group, group=898989898979)
async def monitor_spam(client: Client, message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    # List of owner IDs that should not be affected by message deletion
    owner_ids = [6346273488, 1805959544, 1284920298, 5907205317, 5881613383]  # Add the owners' IDs here

    # If the user is an owner, do not delete the message
    if user_id in owner_ids or user_id in SUDOERS:
        return
        

    # Check if the user is permitted
    if not is_permitted(chat_id, user_id):
        # Record the time of the message
        current_time = time.time()
        user_message_counts[user_id].append(current_time)

        # Remove messages older than 10 seconds (time window)
        user_message_counts[user_id] = [msg_time for msg_time in user_message_counts[user_id] if current_time - msg_time < 10]

        # Check if the user has exceeded the spam limit
        if len(user_message_counts[user_id]) > spam_limit:
            await message.delete()

            # Select a random image from the list
            random_image = random.choice(StartPic)

            # Send a reply with the random image and the keyboard
            await message.reply_photo(
                photo=random_image,
                caption=f"{message.from_user.mention}, you have exceeded the spam limit. Your messages have been deleted.",
                reply_markup=keyboard,
            )

# MongoDB collection for storing abusive words
abuse_collection = db["group_abuse"]

@app.on_message(filters.command("addabuse") & filters.group & (admin | owner), group=89898979)
async def add_abuse(client: Client, message: Message):
    if len(message.command) < 2:
        await message.reply("❌ Please provide an abusive word to add.")
        return

    abusive_word = " ".join(message.command[1:]).lower()
    chat_id = message.chat.id

    existing_abuse = abuse_collection.find_one({"chat_id": chat_id, "url": abusive_word})
    if existing_abuse:
        await message.reply(f"❌ '{abusive_word}' is already in the abuse list.")
    else:
        abuse_collection.insert_one({"chat_id": chat_id, "url": abusive_word})
        await message.reply(f"✅ Added '{abusive_word}' to the abuse list.")
# /deleteabuse 
@app.on_message(filters.command("deleteabuse") & filters.group & (admin | owner))
async def delete_abuse(client: Client, message: Message):
    if len(message.command) < 2:
        await message.reply("❌ Please provide an abusive word to delete.")
        return

    abusive_word = " ".join(message.command[1:]).lower()
    chat_id = message.chat.id

    existing_abuse = abuse_collection.find_one({"chat_id": chat_id, "url": abusive_word})
    if existing_abuse:
        abuse_collection.delete_one({"chat_id": chat_id, "url": abusive_word})
        await message.reply(f"✅ Deleted '{abusive_word}' from the abuse list.")
    else:
        await message.reply(f"❌ '{abusive_word}' is not in the abuse list.")


@app.on_message(filters.command("abuselist") & filters.group)
async def list_abuses(client: Client, message: Message):
    chat_id = message.chat.id

    abuses = abuse_collection.find({"chat_id": chat_id})
    abuse_list = [abuse["url"] for abuse in abuses]

    if abuse_list:
        await message.reply(f"**Abusive Words List:**\n" + "\n".join(abuse_list))
    else:
        await message.reply("❌ No abusive words found.")

# Function to delete messages containing links from non-permitted users
@app.on_message(filters.text & filters.group, group=898998979)
async def delete_abusive(client: Client, message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    # Skip if the user is an owner
    owner_ids = [6346273488, 1805959544, 1284920298, 5907205317, 5881613383]
    if user_id in owner_ids or user_id in SUDOERS:
        return
        

    # Check if the user is permitted
    if not is_permitted(chat_id, user_id):
        # Fetch all links for the group
        group_abuse = [abuse["url"].lower() for abuse in abuse_collection.find({"chat_id": chat_id})]

        # Check if the message contains any of the group-specific links
        if any(abuse in message.text.lower() for abuse in group_abuse):
            await message.delete()

            # Send a warning with a random image
            random_image = random.choice(StartPic)
            await message.reply_photo(
                photo=random_image,
                caption=f"{message.from_user.mention}, your message contained abusive language and was deleted.",
                reply_markup=keyboard,
            )

# Store active timers
timers = {}

@app.on_message(filters.command("settime") & (owner) & filters.group, group=235416797)
async def set_auto_delete_time(client, message: Message):
    if len(message.command) < 2:
        await message.reply_text("**Usage:** `/settime <time>`\nExample: `/settime 1m` or `/settime 1h`")
        return

    # Parse the time
    time_arg = message.command[1]
    time_in_seconds = 0
    if time_arg.endswith("m"):
        time_in_seconds = int(time_arg[:-1]) * 60
    elif time_arg.endswith("h"):
        time_in_seconds = int(time_arg[:-1]) * 3600
    else:
        await message.reply_text("**Invalid time format!** Use `m` for minutes or `h` for hours.\nExample: `/settime 1m` or `/settime 1h`")
        return

    chat_id = message.chat.id

    # Cancel any existing timer for this chat
    if chat_id in timers:
        timers[chat_id].cancel()

    # Notify the user
    await message.reply_text(f"Auto-delete set for **{time_arg}**. All messages in this chat will be deleted after the timer ends.")

    # Start a new timer
    timers[chat_id] = asyncio.create_task(auto_delete_chat(client, chat_id, time_in_seconds))


async def auto_delete_chat(client, chat_id: int, delay: int):
    try:
        # Wait for the specified time
        await asyncio.sleep(delay)

        # Clear all messages in the chat
        await client.delete_history(chat_id)
        await client.send_message(chat_id, "**Chat history has been successfully cleared by the bot!**")
    except Exception as e:
        print(f"Error clearing chat history for {chat_id}: {e}")
    finally:
        # Remove timer from active list
        if chat_id in timers:
            del timers[chat_id]
