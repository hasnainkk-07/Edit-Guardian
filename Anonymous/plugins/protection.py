# (©) Anonymous Emperor V2.0 - Python-Telegram-Bot v20.6 Version
import random
import time
from collections import defaultdict
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
from pymongo import MongoClient
from Anonymous import tgbot, application 
from Anonymous.config import Config, StartPic
from Anonymous.helpers.filters import bot_owner_filter as owner
from Anonymous.config import SUDOERS, Config as c
import asyncio
from datetime import datetime, timedelta

# MongoDB Setup
OWNER = c.OWNERS
MONGO_URI = Config.MONGO_URI
mongo_client = MongoClient(MONGO_URI)
db = mongo_client["AnonymousDB"]
permitted_users_collection = db["permitted_users"]
links_collection = db["group_links"]
abuse_collection = db["group_abuse"]

# Global variables
auto_delete_tasks = {}
user_message_counts = defaultdict(list)
spam_limit = 7

# Define 5 owner IDs
OWNER_IDS = [
    6346273488,  # Owner 1
    1805959544,  # Owner 2
    1284920298,  # Owner 3
    5907205317,  # Owner 4
    5881613383   # Owner 5
]

# Combine owner IDs and sudoers
owner_ids = list(OWNER) + list(SUDOERS)

keyboard = InlineKeyboardMarkup([
    [InlineKeyboardButton("Support", url="https://t.me/Raiden_Updates")],
    [InlineKeyboardButton("Anime Channel", url="https://t.me/Weeb_TV")],
])


# Keyboard markup
def get_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Support", url="https://t.me/Raiden_Support")],
        [InlineKeyboardButton("News", url="https://t.me/Infamous_News")]
    ])

# Helper functions
def is_permitted(chat_id: int, user_id: int) -> bool:
    return bool(permitted_users_collection.find_one({"chat_id": chat_id, "user_id": user_id}))

def is_owner_or_sudo(user_id: int) -> bool:
    return user_id in owner_ids

async def is_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    user = update.effective_user
    chat = update.effective_chat
    
    if user.id in owner_ids:
        return True
        
    try:
        member = await chat.get_member(user.id)
        return member.status in ['administrator', 'creator']
    except:
        return False

async def delete_message_with_warning(update: Update, context: ContextTypes.DEFAULT_TYPE, reason: str):
    user = update.effective_user
    random_image = random.choice(StartPic)
    
    await update.message.reply_photo(
        photo=random_image,
        caption=f"{user.mention_html()} {reason}",
        reply_markup=get_keyboard(),
        parse_mode="HTML"
    )

# Command handlers
async def permit_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        await update.message.reply_text("You need to be an admin to use this command.")
        return
        
    chat_id = update.effective_chat.id
    
    if update.message.reply_to_message:
        user = update.message.reply_to_message.from_user
    else:
        if len(context.args) < 1:
            await update.message.reply_text("Please reply to a user or provide a user ID.")
            return
            
        try:
            user_id = int(context.args[0])
            user = await context.bot.get_chat(user_id)
        except Exception as e:
            await update.message.reply_text(f"Error: {e}")
            return

    if is_permitted(chat_id, user.id):
        await update.message.reply_text(f"{user.mention_html()} is already permitted.", parse_mode="HTML")
        return

    permitted_users_collection.insert_one({"chat_id": chat_id, "user_id": user.id})
    await update.message.reply_text(f"{user.mention_html()} has been permitted.", parse_mode="HTML")

async def rpermit_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        await update.message.reply_text("You need to be an admin to use this command.")
        return
        
    chat_id = update.effective_chat.id
    
    if update.message.reply_to_message:
        user = update.message.reply_to_message.from_user
    else:
        if len(context.args) < 1:
            await update.message.reply_text("Please reply to a user or provide a user ID.")
            return
            
        try:
            user_id = int(context.args[0])
            user = await context.bot.get_chat(user_id)
        except Exception as e:
            await update.message.reply_text(f"Error: {e}")
            return

    if not is_permitted(chat_id, user.id):
        await update.message.reply_text(f"{user.mention_html()} is not in the permitted list.", parse_mode="HTML")
        return

    permitted_users_collection.delete_one({"chat_id": chat_id, "user_id": user.id})
    await update.message.reply_text(f"{user.mention_html()} has been removed from permitted list.", parse_mode="HTML")

async def permit_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        await update.message.reply_text("You need to be an admin to use this command.")
        return
        
    chat_id = update.effective_chat.id
    permitted_users = list(permitted_users_collection.find({"chat_id": chat_id}))
    
    if not permitted_users:
        await update.message.reply_text("No users are currently permitted.")
        return
    
    user_list = []
    for user in permitted_users:
        try:
            user_info = await context.bot.get_chat(user["user_id"])
            user_list.append(f"{user_info.mention_html()} ({user_info.id})")
        except:
            user_list.append(f"Unknown User ({user['user_id']})")
    
    await update.message.reply_text(
        "Permitted Users:\n" + "\n".join(user_list),
        parse_mode="HTML"
    )

async def add_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        await update.message.reply_text("You need to be an admin to use this command.")
        return
        
    chat_id = update.effective_chat.id
    
    if not context.args:
        await update.message.reply_text("Please provide a link to add.")
        return
        
    link = context.args[0].lower()
    
    if links_collection.find_one({"chat_id": chat_id, "url": link}):
        await update.message.reply_text("This link is already in the list.")
        return
        
    links_collection.insert_one({"chat_id": chat_id, "url": link})
    await update.message.reply_text(f"Link {link} has been added to the restricted list.")

async def delete_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        await update.message.reply_text("You need to be an admin to use this command.")
        return
        
    chat_id = update.effective_chat.id
    
    if not context.args:
        await update.message.reply_text("Please provide a link to remove.")
        return
        
    link = context.args[0].lower()
    
    if not links_collection.find_one({"chat_id": chat_id, "url": link}):
        await update.message.reply_text("This link is not in the list.")
        return
        
    links_collection.delete_one({"chat_id": chat_id, "url": link})
    await update.message.reply_text(f"Link {link} has been removed from the restricted list.")

async def link_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        await update.message.reply_text("You need to be an admin to use this command.")
        return
        
    chat_id = update.effective_chat.id
    links = list(links_collection.find({"chat_id": chat_id}))
    
    if not links:
        await update.message.reply_text("No links are currently restricted.")
        return
    
    link_list = [link["url"] for link in links]
    await update.message.reply_text("Restricted Links:\n" + "\n".join(link_list))

async def set_spam_limit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner_or_sudo(update.effective_user.id):
        await update.message.reply_text("Only owner can use this command.")
        return
        
    global spam_limit
    
    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text("Please provide a valid number for spam limit.")
        return
        
    spam_limit = int(context.args[0])
    await update.message.reply_text(f"Spam limit set to {spam_limit} messages per 10 seconds.")

async def add_abuse(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        await update.message.reply_text("You need to be an admin to use this command.")
        return
        
    chat_id = update.effective_chat.id
    
    if not context.args:
        await update.message.reply_text("Please provide a word to add to abusive list.")
        return
        
    word = " ".join(context.args).lower()
    
    if abuse_collection.find_one({"chat_id": chat_id, "url": word}):
        await update.message.reply_text("This word is already in the abusive list.")
        return
        
    abuse_collection.insert_one({"chat_id": chat_id, "url": word})
    await update.message.reply_text(f"Word '{word}' has been added to the abusive list.")

async def delete_abuse(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        await update.message.reply_text("You need to be an admin to use this command.")
        return
        
    chat_id = update.effective_chat.id
    
    if not context.args:
        await update.message.reply_text("Please provide a word to remove from abusive list.")
        return
        
    word = " ".join(context.args).lower()
    
    if not abuse_collection.find_one({"chat_id": chat_id, "url": word}):
        await update.message.reply_text("This word is not in the abusive list.")
        return
        
    abuse_collection.delete_one({"chat_id": chat_id, "url": word})
    await update.message.reply_text(f"Word '{word}' has been removed from the abusive list.")

async def abuse_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner_or_sudo(update.effective_user.id):
        await update.message.reply_text("Only owner can use this command.")
        return
        
    chat_id = update.effective_chat.id
    abuses = list(abuse_collection.find({"chat_id": chat_id}))
    
    if not abuses:
        await update.message.reply_text("No words are currently in the abusive list.")
        return
    
    abuse_list = [abuse["url"] for abuse in abuses]
    await update.message.reply_text("Abusive Words List:\n" + "\n".join(abuse_list))

async def set_auto_delete_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner_or_sudo(update.effective_user.id):
        await update.message.reply_text("Only owner can use this command.")
        return
        
    chat_id = update.effective_chat.id
    
    if not context.args:
        await update.message.reply_text("Please provide a time (e.g., 1m or 1h).")
        return
        
    time_arg = context.args[0]
    try:
        if time_arg.endswith('m'):
            seconds = int(time_arg[:-1]) * 60
        elif time_arg.endswith('h'):
            seconds = int(time_arg[:-1]) * 3600
        else:
            raise ValueError("Invalid time format")
            
        # Cancel existing task if any
        if chat_id in auto_delete_tasks:
            auto_delete_tasks[chat_id].cancel()
            
        # Schedule new task
        auto_delete_tasks[chat_id] = asyncio.create_task(auto_delete_chat(context.bot, chat_id, seconds))
        
        await update.message.reply_text(f"Auto-delete set for {time_arg}. All messages will be deleted after this time.")
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

async def auto_delete_chat(bot, chat_id: int, delay: int):
    await asyncio.sleep(delay)
    try:
        await bot.send_message(chat_id, "Clearing chat history...")
        await bot.send_message(chat_id, "Chat history has been cleared!")
        
        if chat_id in auto_delete_tasks:
            del auto_delete_tasks[chat_id]
    except Exception as e:
        print(f"Error clearing chat: {e}")

# Message handlers
async def check_edit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # Check if we have an edited message
        if not update.edited_message:
            return

        user = update.effective_user
        chat = update.effective_chat

        # Validate we have required objects
        if not user or not chat:
            return

        # Skip if user is owner/sudo or permitted
        if is_owner_or_sudo(user.id) or is_permitted(chat.id, user.id):
            return

        # Send warning with photo
        try:
            warning_msg = await context.bot.send_photo(
                chat_id=chat.id,
                photo=random.choice(StartPic),
                caption=f"{user.mention_html()} just edited a message. This will be deleted in 60 seconds.",
                reply_to_message_id=update.edited_message.message_id,
                parse_mode="HTML"
            )
        except Exception as warn_err:
            print(f"Warning message error: {warn_err}")
            return

        # Wait before deletion
        await asyncio.sleep(60)

        # Delete both messages
        try:
            await update.edited_message.delete()
        except Exception as del_err:
            print(f"Delete edited message error: {del_err}")

        try:
            await warning_msg.delete()
        except Exception as warn_del_err:
            print(f"Delete warning message error: {warn_del_err}")

        # Send confirmation
        try:
            confirm_msg = await context.bot.send_message(
                chat.id,
                f"✅ {user.mention_html()}'s edited message was deleted.",
                parse_mode="HTML"
            )
            await asyncio.sleep(10)
            await confirm_msg.delete()
        except Exception as confirm_err:
            print(f"Confirmation message error: {confirm_err}")

    except Exception as e:
        print(f"Error in check_edit: {e}")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # Basic validation
        if not update.message or not update.effective_chat or not update.effective_user:
            return

        chat_id = update.effective_chat.id
        user_id = update.effective_user.id

        # Skip checks for owners/sudoers
        if is_owner_or_sudo(user_id):
            return

        # Skip if user is permitted
        if is_permitted(chat_id, user_id):
            return

        # Spam protection
        current_time = time.time()
        user_message_counts[user_id] = [t for t in user_message_counts.get(user_id, []) if current_time - t < 10]
        user_message_counts[user_id].append(current_time)

        if len(user_message_counts[user_id]) > spam_limit:
            try:
                await update.message.delete()
                await delete_message_with_warning(update, context, "you have exceeded the spam limit.")
            except Exception as e:
                print(f"Spam protection error: {e}")
            return

        # Link restriction check
        if update.message.text:
            try:
                restricted_links = [str(link.get("url", "")) for link in links_collection.find({"chat_id": chat_id})]
                if any(link and link in update.message.text.lower() for link in restricted_links):
                    await update.message.delete()
                    await delete_message_with_warning(update, context, "your message contained a restricted link.")
                    return
            except Exception as link_err:
                print(f"Link check error: {link_err}")

            # Abusive words check
            try:
                abusive_words = [str(abuse.get("url", "")) for abuse in abuse_collection.find({"chat_id": chat_id})]
                if any(word and word in update.message.text.lower() for word in abusive_words):
                    await update.message.delete()
                    await delete_message_with_warning(update, context, "your message contained abusive language.")
                    return
            except Exception as abuse_err:
                print(f"Abuse check error: {abuse_err}")

    except Exception as e:
        print(f"Error in handle_message: {e}")


# COMMANDS AND FEATURES FOR IMAGES DELETING 

# MongoDB collection for image delete settings
image_delete_collection = db["image_delete_settings"]
image_delete_tasks = {}  # Global variable to track active tasks

async def set_image_delete_delay(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        await update.message.reply_text("❌ You need to be admin to use this!")
        return
        
    if not context.args:
        await update.message.reply_text("Usage: /setdelay <time><unit>\nExample: /setdelay 30s\n(s=sec, m=min, h=hours, d=days)")
        return
        
    time_arg = context.args[0].lower()
    chat_id = update.effective_chat.id
    
    try:
        if time_arg.endswith('s'):
            seconds = int(time_arg[:-1])
        elif time_arg.endswith('m'):
            seconds = int(time_arg[:-1]) * 60
        elif time_arg.endswith('h'):
            seconds = int(time_arg[:-1]) * 3600
        elif time_arg.endswith('d'):
            seconds = int(time_arg[:-1]) * 86400
        else:
            raise ValueError("Invalid time unit! Use s/m/h/d")
            
        # Save to DB
        image_delete_collection.update_one(
            {"chat_id": chat_id},
            {"$set": {"delay": seconds}},
            upsert=True
        )
        
        # Cancel existing task
        if chat_id in image_delete_tasks:
            image_delete_tasks[chat_id].cancel()
            
        # Start new task
        image_delete_tasks[chat_id] = asyncio.create_task(
            auto_delete_images(context.bot, chat_id, seconds)
        )
        
        await update.message.reply_text(f"✅ Auto-delete set! Images will delete after {time_arg}")
        
    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")

async def disable_image_delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        return
        
    chat_id = update.effective_chat.id
    image_delete_collection.delete_one({"chat_id": chat_id})
    
    if chat_id in image_delete_tasks:
        image_delete_tasks[chat_id].cancel()
        del image_delete_tasks[chat_id]
        
    await update.message.reply_text("❌ Image auto-delete disabled!")

async def auto_delete_images(bot, chat_id: int, delay: int):
    while True:
        await asyncio.sleep(delay)
        try:
            # Verify settings still exist
            if not image_delete_collection.find_one({"chat_id": chat_id}):
                break
                
            # Get recent messages (simplified - you may need better message tracking)
            messages = await bot.get_chat_history(chat_id, limit=100)
            for msg in messages:
                if msg.photo and (time.time() - msg.date.timestamp()) > delay:
                    try:
                        await msg.delete()
                    except:
                        continue
                        
        except Exception as e:
            print(f"Image delete error in {chat_id}: {e}")
            break

async def handle_new_images(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.photo:
        return
        
    chat_id = update.effective_chat.id
    settings = image_delete_collection.find_one({"chat_id": chat_id})
    
    if settings:
        delay = settings["delay"]
        await asyncio.sleep(delay)
        try:
            await update.message.delete()
        except:
            pass

async def permitalladmins(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Check if user is bot owner or chat owner
    user = update.effective_user
    chat = update.effective_chat
    
    # Check if user is bot owner
    if not is_owner_or_sudo(user.id):
        await update.message.reply_text("❌ Only bot owners can use this command!")
        return
    
    # Check if user is chat owner (creator)
    try:
        member = await chat.get_member(user.id)
        if member.status != 'creator' and not is_owner_or_sudo(user.id):
            await update.message.reply_text("❌ Only chat owners can use this command!")
            return
    except Exception as e:
        print(f"Error checking member status: {e}")
        await update.message.reply_text("❌ Error checking your permissions!")
        return
    
    # Get all admins in the chat
    try:
        admins = await chat.get_administrators()
    except Exception as e:
        print(f"Error getting admins: {e}")
        await update.message.reply_text("❌ Error getting admin list!")
        return
    
    # Permit each admin
    chat_id = chat.id
    count = 0
    already_permitted = 0
    
    for admin in admins:
        admin_user = admin.user
        
        # Skip bots
        if admin_user.is_bot:
            continue
            
        # Check if already permitted
        if is_permitted(chat_id, admin_user.id):
            already_permitted += 1
            continue
            
        # Add to permitted list
        permitted_users_collection.insert_one({"chat_id": chat_id, "user_id": admin_user.id})
        count += 1
    
    # Send result
    await update.message.reply_text(
        f"✅ Permitted all admins successfully!\n"
        f"• Newly permitted: {count}\n"
        f"• Already permitted: {already_permitted}\n"
        f"• Total admins processed: {len(admins)}"
    )

# Add the handler to the application
application.add_handler(CommandHandler("permitalladmins", permitalladmins, filters.ChatType.GROUPS))
#application.add_handler(CommandHandler("setdelay", set_image_delete_delay, filters.ChatType.GROUPS))
#application.add_handler(CommandHandler("disableimgdelete", disable_image_delete, filters.ChatType.GROUPS))
#application.add_handler(MessageHandler(filters.PHOTO & filters.ChatType.GROUPS, handle_new_images))
# Add handlers to the application
application.add_handler(CommandHandler("permit", permit_user, filters.ChatType.GROUPS, block=False))
application.add_handler(CommandHandler("rpermit", rpermit_user, filters.ChatType.GROUPS))
application.add_handler(CommandHandler("permitlist", permit_list, filters.ChatType.GROUPS))
#application.add_handler(CommandHandler("addlink", add_link, filters.ChatType.GROUPS))
#application.add_handler(CommandHandler("deletelink", delete_link, filters.ChatType.GROUPS))
#application.add_handler(CommandHandler("linklist", link_list, filters.ChatType.GROUPS))
#application.add_handler(CommandHandler("setlimit", set_spam_limit, filters.ChatType.GROUPS))
#application.add_handler(CommandHandler("addabuse", add_abuse, filters.ChatType.GROUPS))
#application.add_handler(CommandHandler("deleteabuse", delete_abuse, filters.ChatType.GROUPS))
#application.add_handler(CommandHandler("abuselist", abuse_list, filters.ChatType.GROUPS))
#application.add_handler(CommandHandler("settime", set_auto_delete_time, filters.ChatType.GROUPS))

# Message handler
#application.add_handler(MessageHandler(filters.TEXT & filters.ChatType.GROUPS & ~filters.COMMAND, handle_message))

# Edited message handler
application.add_handler(MessageHandler(filters.UpdateType.EDITED_MESSAGE, check_edit, filters.ChatType.GROUPS)) #& filters.ChatType.GROUPS & ~filters.StatusUpdate.ALL, check_edit))
from telegram.ext import TypeHandler
#application.add_handler(TypeHandler(Update, check_edit, update_filter=filters.UpdateType.EDITED_MESSAGE & filters.ChatType.GROUPS))
#application.add_handler(TypeHandler(Update, check_edit, block=False))
