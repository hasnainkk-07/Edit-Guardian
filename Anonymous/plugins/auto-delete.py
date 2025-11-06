from pyrogram import Client, filters
from pyrogram.types import Message
import re
import asyncio
from Anonymous import ubot, app  # Importing your UserBot client
from Anonymous.helpers.filters import owner_filter as admin, owner

# Dictionary to store deletion timers
auto_delete_tasks = {}

async def delete_all_messages(chat_id: int):
    """Delete all messages in a chat using the UserBot"""
    try:
        # Get all message IDs in the chat
        message_ids = []
        async for message in ubot.get_chat_history(chat_id):
            message_ids.append(message.id)
            if len(message_ids) >= 100:  # Delete in batches of 100
                await ubot.delete_messages(chat_id, message_ids)
                message_ids = []
        
        # Delete any remaining messages
        if message_ids:
            await ubot.delete_messages(chat_id, message_ids)
            
        await ubot.send_message(chat_id, "✅ All messages have been automatically deleted as per schedule.")
    except Exception as e:
        print(f"Error deleting messages in chat {chat_id}: {e}")

async def schedule_deletion(chat_id: int, interval: int):
    """Schedule periodic message deletion"""
    while chat_id in auto_delete_tasks and auto_delete_tasks[chat_id]["running"]:
        await asyncio.sleep(interval)
        if chat_id in auto_delete_tasks and auto_delete_tasks[chat_id]["running"]:
            await delete_all_messages(chat_id)

@ubot.on_message(filters.command("setdelete") & filters.group & (admin | owner))
async def set_auto_delete(_, message: Message):
    """Set automatic message deletion schedule"""
    chat_id = message.chat.id
    
    if len(message.command) < 2:
        await message.reply("**Usage:** `/setdelete <time>`\n"
                          "Examples:\n"
                          "• `/setdelete 30s` - 30 seconds\n"
                          "• `/setdelete 5m` - 5 minutes\n"
                          "• `/setdelete 2h` - 2 hours\n"
                          "• `/setdelete 1d` - 1 day")
        return
    
    time_arg = message.command[1].lower()
    match = re.match(r"^(\d+)([smhd])$", time_arg)
    
    if not match:
        await message.reply("❌ Invalid time format. Use: 30s, 5m, 2h, 1d")
        return
    
    amount = int(match.group(1))
    unit = match.group(2)
    
    # Convert to seconds
    if unit == "s":
        interval = amount
    elif unit == "m":
        interval = amount * 60
    elif unit == "h":
        interval = amount * 3600
    elif unit == "d":
        interval = amount * 86400
    else:
        await message.reply("❌ Invalid time unit. Use s, m, h, or d")
        return
    
    # Cancel any existing timer
    if chat_id in auto_delete_tasks:
        auto_delete_tasks[chat_id]["running"] = False
        if "task" in auto_delete_tasks[chat_id]:
            auto_delete_tasks[chat_id]["task"].cancel()
    
    # Create new timer
    auto_delete_tasks[chat_id] = {
        "running": True,
        "interval": interval,
        "task": asyncio.create_task(schedule_deletion(chat_id, interval))
    }
    
    # Human-readable time
    time_units = {
        "s": "second(s)",
        "m": "minute(s)",
        "h": "hour(s)",
        "d": "day(s)"
    }
    
    await message.reply(f"✅ Auto-delete set! All messages will be deleted every {amount} {time_units[unit]}.")

@ubot.on_message(filters.command("stopdelete") & filters.group & (admin | owner))
async def stop_auto_delete(_, message: Message):
    """Stop automatic message deletion"""
    chat_id = message.chat.id
    
    if chat_id in auto_delete_tasks:
        auto_delete_tasks[chat_id]["running"] = False
        if "task" in auto_delete_tasks[chat_id]:
            auto_delete_tasks[chat_id]["task"].cancel()
        del auto_delete_tasks[chat_id]
        await message.reply("❌ Auto-delete has been stopped for this group.")
    else:
        await message.reply("ℹ️ No active auto-delete schedule found for this group.")
