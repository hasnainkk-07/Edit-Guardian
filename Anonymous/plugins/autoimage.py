import asyncio
import logging
from datetime import datetime
from pyrogram import Client, filters
from pyrogram.types import Message, ChatPrivileges
from pyrogram.enums import MessagesFilter
from Anonymous import ubot, OWNER_ID as OWNER_IDS, app
from Anonymous.helpers.filters import owner, owner_filter

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [Anonymous] - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('auto_delete.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Active deletion tasks
active_deletions = {}

# Supported filters for search_messages
MEDIA_TYPES = {
    'photo': MessagesFilter.PHOTO,
    'video': MessagesFilter.VIDEO,
    'gif': MessagesFilter.ANIMATION,
    'document': MessagesFilter.DOCUMENT,
    'audio': MessagesFilter.AUDIO,
 #   'voice': MessagesFilter.VOICE,
    'video_note': MessagesFilter.VIDEO_NOTE
}

# Manual filters (not supported by MessagesFilter)
MANUAL_TYPES = ['sticker']

async def setup_userbot(chat_id: int):
    """Ensure UserBot is in chat and has necessary permissions"""
    try:
        me = await ubot.get_chat_member(chat_id, "me")
        if me.privileges and me.privileges.can_delete_messages:
            return True
    except:
        pass
    try:
        invite_link = await app.export_chat_invite_link(chat_id)
        await ubot.join_chat(invite_link)
        await ubot.promote_chat_member(
            chat_id,
            "me",
            privileges=ChatPrivileges(
                can_delete_messages=True,
                can_restrict_members=True,
                can_invite_users=True
            )
        )
        return True
    except Exception as e:
        logger.error(f"UserBot setup failed: {str(e)}")
        return False

async def media_deletion_worker(chat_id: int, delay: int, media_types: list):
    """Worker to delete media older than delay"""
    while chat_id in active_deletions:
        try:
            now = datetime.utcnow()
            for media_type in media_types:
                if media_type in MEDIA_TYPES:
                    async for message in ubot.search_messages(chat_id, filter=MEDIA_TYPES[media_type], limit=200):
                        if (now - message.date).total_seconds() >= delay:
                            try:
                                await message.delete()
                                await asyncio.sleep(0.3)
                            except Exception as e:
                                logger.error(f"Delete failed: {e}")
                elif media_type == "sticker":
                    async for message in ubot.search_messages(chat_id, limit=200):
                        if message.sticker and (now - message.date).total_seconds() >= delay:
                            try:
                                await message.delete()
                                await asyncio.sleep(0.3)
                            except Exception as e:
                                logger.error(f"Sticker delete failed: {e}")
            await asyncio.sleep(60)
        except Exception as e:
            logger.error(f"Worker error: {e}")
            await asyncio.sleep(10)

@app.on_message(filters.command("autodelete") & (owner | owner_filter), group=9999)
async def start_autodelete(_, message: Message):
    chat_id = message.chat.id
    try:
        args = message.text.split()
        if len(args) < 2:
            raise ValueError("Missing time parameter (e.g. 30s, 2m, 1h)")

        time_arg = args[1].lower()
        if time_arg.endswith('s'):
            delay = int(time_arg[:-1])
        elif time_arg.endswith('m'):
            delay = int(time_arg[:-1]) * 60
        elif time_arg.endswith('h'):
            delay = int(time_arg[:-1]) * 3600
        elif time_arg.endswith('d'):
            delay = int(time_arg[:-1]) * 86400
        else:
            raise ValueError("Invalid time format (use s/m/h/d)")

        # Parse media types
        all_media = list(MEDIA_TYPES.keys()) + MANUAL_TYPES
        media_types = [m for m in args[2:] if m in all_media] or list(MEDIA_TYPES.keys())

        # Setup UserBot
        if not await setup_userbot(chat_id):
            return await message.reply("❌ UserBot join or promotion failed.")

        # Cancel existing task if any
        if chat_id in active_deletions:
            active_deletions[chat_id].cancel()

        # Start deletion task
        active_deletions[chat_id] = asyncio.create_task(
            media_deletion_worker(chat_id, delay, media_types)
        )

        await message.reply(
            f"✅ Auto-delete enabled\n"
            f"• Delay: <b>{time_arg}</b>\n"
            f"• Media Types: <code>{', '.join(media_types)}</code>\n"
            f"• Old media will be deleted every minute."
        )

    except Exception as e:
        await message.reply(f"❌ Error: {e}\nUsage: /autodelete 30s [photo video sticker]")

@app.on_message(filters.command("stopautodelete") & (owner | owner_filter), group=9999)
async def stop_autodelete(_, message: Message):
    chat_id = message.chat.id
    if chat_id in active_deletions:
        active_deletions[chat_id].cancel()
        del active_deletions[chat_id]
        await message.reply("⛔ Auto-delete stopped.")
    else:
        await message.reply("ℹ️ No auto-delete is active in this chat.")

@app.on_message(filters.command("inviteubot") & (owner | owner_filter), group=9999)
async def invite_userbot_cmd(_, message: Message):
    chat_id = message.chat.id
    if await setup_userbot(chat_id):
        await message.reply("✅ UserBot joined and promoted.")
    else:
        await message.reply("❌ Failed to setup UserBot.")

@app.on_message(filters.command("join"), group=9999)
async def join_cmd(_, message: Message):
    if len(message.command) < 2:
        return await message.reply("❌ Usage: /join <t.me/link>")
    link = message.text.split(None, 1)[1]
    try:
        await ubot.join_chat(link)
        await message.reply(f"✅ UserBot joined: {link}")
    except Exception as e:
        logger.error(f"Join error: {e}")
        await message.reply(f"❌ Failed to join: {e})to join: {e}")
