import os
import time
import random
import asyncio
from pathlib import Path

from pyrogram import Client
from pyrogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ChatMemberStatus, ParseMode

from pymongo import MongoClient
from Anonymous.bot import handler
from Anonymous import app, ubot, filters 

from Anonymous.config import StartPic, Config

# === Setup ===
BLACKLIST_FILE = Path("blacklist.txt")

if not BLACKLIST_FILE.exists():
    with open(BLACKLIST_FILE, "w") as f:
        f.write("bc\nmc\nfuck\n")

MONGO_URI = Config.MONGO_URI
mongo_client = MongoClient(MONGO_URI)
db = mongo_client["AnonymousDB"]

abuse_collection = db["abusive_words"]
permitted_users_collection = db["permitted_users"]
settings_collection = db["group_settings"]

owner_ids = [6346273488, 1805959544, 1284920298, 5907205317, 5881613383]

# === Functions ===
def sync_blacklist_with_mongo():
    with open(BLACKLIST_FILE, "r") as f:
        words = [line.strip().lower() for line in f if line.strip()]
    for word in words:
        if not abuse_collection.find_one({"word": word}):
            abuse_collection.insert_one({
                "word": word,
                "source": "blacklist.txt",
                "global": True
            })

def is_abuse_detection_enabled(chat_id: int) -> bool:
    data = settings_collection.find_one({"chat_id": chat_id})
    return data.get("abuse_detection", True) if data else True

def is_permitted(chat_id: int, user_id: int) -> bool:
    return bool(permitted_users_collection.find_one({"chat_id": chat_id, "user_id": user_id}))

sync_blacklist_with_mongo()

# === Abuse On/Off Toggle ===
#@app.on_message(filters.command("abuse") & filters.group)
@handler("abuse")
async def abuse_toggle(client: Client, message: Message):
    user_id = message.from_user.id
    chat_id = message.chat.id

    member = await client.get_chat_member(chat_id, user_id)
    if member.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER] and user_id not in owner_ids:
        return await message.reply("❌ Only admins or owners can use this command.")

    if len(message.command) < 2:
        status = "enabled" if is_abuse_detection_enabled(chat_id) else "disabled"
        return await message.reply(
            f"⚙️ Abuse detection is currently *{status}*.\nUse `/abuse on` or `/abuse off`.",
            parse_mode=ParseMode.MARKDOWN
        )

    state = message.command[1].lower()
    if state == "on":
        settings_collection.update_one({"chat_id": chat_id}, {"$set": {"abuse_detection": True}}, upsert=True)
        await message.reply("✅ Abuse detection has been *enabled*.", parse_mode=ParseMode.MARKDOWN)
    elif state == "off":
        settings_collection.update_one({"chat_id": chat_id}, {"$set": {"abuse_detection": False}}, upsert=True)
        await message.reply("❌ Abuse detection has been *disabled*.", parse_mode=ParseMode.MARKDOWN)
    else:
        await message.reply("Usage:\n/abuse on\n/abuse off")

# === Owner-only Word Management ===
#@app.on_message(filters.command(["newword"], dev_cmd=True)) #& filters.user(owner_ids), group=1001)
@handler("newword", dev_cmd=True)
async def add_abusive_word(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply("Usage: /newword <word>")

    word = message.command[1].lower()
    if abuse_collection.find_one({"word": word}):
        return await message.reply(f"'{word}' is already in the abusive list.")

    abuse_collection.insert_one({
        "word": word,
        "source": "manual",
        "global": True,
        "added_by": message.from_user.id,
        "timestamp": time.time()
    })

    with open(BLACKLIST_FILE, "a") as f:
        f.write(f"{word}\n")

    await message.reply(f"✅ Added '{word}' to the abusive words list.")

#@app.on_message(filters.command(["remword"], dev_cmd=True)) # & filters.user(owner_ids), group=1002)
@handler("remword", dev_cmd=True)
async def remove_abusive_word(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply("Usage: /remword <word>")

    word = message.command[1].lower()
    result = abuse_collection.delete_one({"word": word})

    if result.deleted_count == 0:
        return await message.reply(f"'{word}' not found in the list.")

    with open(BLACKLIST_FILE, "r") as f:
        words = [line.strip() for line in f if line.strip() != word]
    with open(BLACKLIST_FILE, "w") as f:
        f.write("\n".join(words) + "\n")

    await message.reply(f"🗑 Removed '{word}' from the abusive words list.")

#@app.on_message(filters.command(["wordlist"], dev_cmd=True)) #& filters.user(owner_ids), group=1003)
@handler("wordlist", gc_admin=True, dev_cmd=True)
async def get_wordlist(client: Client, message: Message):
    words = [doc["word"] for doc in abuse_collection.find({}, {"word": 1})]

    if not words:
        return await message.reply("⚠️ No abusive words found.")

    filename = "abusive_words_list.txt"
    with open(filename, "w") as f:
        f.write("\n".join(words))

    await message.reply_document(filename, caption="📝 Abusive Words List")
    os.remove(filename)

# === Abusive Message Handler ===
@app.on_message(filters.text & filters.group)
async def check_abusive_messages(client: Client, message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    if user_id in owner_ids or is_permitted(chat_id, user_id):
        return

    if not is_abuse_detection_enabled(chat_id):
        return

    message_text = message.text.lower()
    abusive_words = [doc["word"] for doc in abuse_collection.find({}, {"word": 1})]
    found_words = [word for word in abusive_words if word in message_text]

    if found_words:
        await message.delete()
        formatted = ", ".join([f"||{w}||" for w in found_words])
        photo = random.choice(StartPic)

        reply = await message.reply_photo(
            photo=photo,
            caption=(
                f"⚠️ **Abusive Language Detected**\n\n"
                f"👤 **User:** {message.from_user.mention}\n"
                f"🚫 **Words Found:** {formatted}\n\n"
                f"Message removed for violating rules."
            ),
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🚫 Report", callback_data="report_abuse")],
                [InlineKeyboardButton("❌ Ban User", callback_data=f"ban_{user_id}")],
                [InlineKeyboardButton("📜 Rules", url="https://t.me/Raiden_Support")]
            ])
        )
        await asyncio.sleep(60)
        try:
            await reply.delete()
        except:
            pass

# === Callback: Ban User ===
@app.on_callback_query(filters.regex(r"^ban_(\d+)$"))
async def ban_user_callback(client: Client, cq: CallbackQuery):
    user_id = int(cq.matches[0].group(1))
    chat = cq.message.chat
    admin = cq.from_user

    member = await client.get_chat_member(chat.id, admin.id)
    if member.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
        return await cq.answer("Only admins can ban users.", show_alert=True)

    try:
        await client.ban_chat_member(chat.id, user_id)
        await cq.message.edit_text(f"🚫 User banned by {admin.mention}")
    except Exception as e:
        await cq.answer(f"Error: {e}", show_alert=True)

# === Callback: Report Abuse ===
@app.on_callback_query(filters.regex("^report_abuse$"))
async def report_abuse_callback(client: Client, cq: CallbackQuery):
    await cq.answer("🚨 Abuse reported to admins.", show_alert=True)
