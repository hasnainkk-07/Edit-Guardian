from Anonymous import app as app, DB_URI, filters
from pyrogram import Client
from Anonymous.bot import handler 
from pyrogram.types import Message
from pymongo import MongoClient
import asyncio
import time

# MongoDB setup
mongo_client = MongoClient(DB_URI)
db = mongo_client["media_auto_delete"]
media_delete_collection = db["settings"]
media_delete_tasks = {}

from pyrogram.enums import ChatMemberStatus

async def is_admin(chat_id: int, user_id: int) -> bool:
    try:
        member = await app.get_chat_member(chat_id, user_id)
        return member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]
    except:
        return False

#@app.on_message(filters.command("setdelay") & filters.group)
@handler("setdelay", extra=filters.group)
async def set_media_delete_delay(client: Client, message: Message):
    if not await is_admin(message.chat.id, message.from_user.id):
        await message.reply_text("❌ You need to be admin to use this!")
        return
        
    if len(message.command) < 2:
        await message.reply_text("Usage: /setdelay <time><unit>\nExample: /setdelay 30s\n(s=sec, m=min, h=hours, d=days)")
        return
        
    time_arg = message.command[1].lower()
    chat_id = message.chat.id
    
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
        media_delete_collection.update_one(
            {"chat_id": chat_id},
            {"$set": {"delay": seconds}},
            upsert=True
        )
        
        # Cancel existing task
        if chat_id in media_delete_tasks:
            media_delete_tasks[chat_id].cancel()
            
        # Start new task
        media_delete_tasks[chat_id] = asyncio.create_task(
            auto_delete_media(client, chat_id, seconds)
        )
        
        await message.reply_text(f"✅ Auto-delete set! All media will delete after {time_arg}")
        
    except Exception as e:
        await message.reply_text(f"Error: {str(e)}")

@app.on_message(filters.command("disablemediadelete") & filters.group)
async def disable_media_delete(client: Client, message: Message):
    if not await is_admin(message.chat.id, message.from_user.id):
        return
        
    chat_id = message.chat.id
    media_delete_collection.delete_one({"chat_id": chat_id})
    
    if chat_id in media_delete_tasks:
        media_delete_tasks[chat_id].cancel()
        del media_delete_tasks[chat_id]
        
    await message.reply_text("❌ Media auto-delete disabled!")

async def auto_delete_media(client: Client, chat_id: int, delay: int):
    while True:
        await asyncio.sleep(delay)
        try:
            # Verify settings still exist
            if not media_delete_collection.find_one({"chat_id": chat_id}):
                break
                
            # Get recent messages
            messages = []
            async for msg in client.get_chat_history(chat_id, limit=100):
                messages.append(msg)
                
            for msg in messages:
                if is_media_message(msg) and (time.time() - msg.date.timestamp()) > delay:
                    try:
                        await msg.delete()
                    except Exception as e:
                        print(f"Failed to delete message: {e}")
                        continue
                        
        except Exception as e:
            print(f"Media delete error in {chat_id}: {e}")
            break

def is_media_message(message: Message) -> bool:
    """Check if message contains any deletable media"""
    return bool(
        message.photo or message.video or message.document or
        message.audio or message.video_note or
        message.sticker or message.animation
    )

@app.on_message(filters.group & (
    filters.photo | filters.video | filters.document |
    filters.audio | filters.video_note | 
    filters.sticker | filters.animation
))
async def handle_new_media(client: Client, message: Message):
    chat_id = message.chat.id
    settings = media_delete_collection.find_one({"chat_id": chat_id})
    
    if settings and is_media_message(message):
        delay = settings["delay"]
        await asyncio.sleep(delay)
        try:
            await message.delete()
        except Exception as e:
            print(f"Failed to delete new media: {e}")
