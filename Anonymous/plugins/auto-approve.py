import asyncio
import logging
from pyrogram import filters
from pyrogram.types import ChatJoinRequest, Message
from pyrogram.errors import FloodWait
from Anonymous import ubot
from Anonymous import OWNER_ID as OWNER_IDS

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Track active chats and processing flags
active_chats = {}
processing = {}

async def bulk_approve(chat_id, user_ids):
    """Approve multiple users at once with flood control"""
    approved = 0
    for user_id in user_ids:
        try:
            await ubot.approve_chat_join_request(chat_id, user_id)
            approved += 1
            logger.info(f"Approved {user_id} in {chat_id}")
            
            # Small delay between approvals to avoid flood
            if approved % 50 == 0:
                await asyncio.sleep(2)
            elif approved % 10 == 0:
                await asyncio.sleep(0.5)
                
        except FloodWait as e:
            logger.warning(f"FloodWait: Sleeping {e.value}s")
            await asyncio.sleep(e.value)
            # Retry current user after wait
            try:
                await ubot.approve_chat_join_request(chat_id, user_id)
                approved += 1
            except Exception as e:
                logger.error(f"Retry failed for {user_id}: {str(e)}")
        except Exception as e:
            logger.error(f"Error approving {user_id}: {str(e)}")
    
    return approved

async def process_pending_requests(chat_id):
    """Process all pending requests quickly"""
    if chat_id in processing and processing[chat_id]:
        return
    
    processing[chat_id] = True
    try:
        logger.info(f"Starting bulk approval for {chat_id}")
        
        # Collect all user IDs first
        user_ids = []
        async for request in ubot.get_chat_join_requests(chat_id):
            user_ids.append(request.user.id)
            # Process in batches of 100
            if len(user_ids) >= 100:
                await bulk_approve(chat_id, user_ids)
                user_ids = []
        
        # Process remaining users
        if user_ids:
            await bulk_approve(chat_id, user_ids)
            
        logger.info(f"Finished processing pending requests for {chat_id}")
    finally:
        processing[chat_id] = False

@ubot.on_message(filters.command("autoapprove") & filters.user(OWNER_IDS))
async def enable_auto_approve(_, message: Message):
    chat_id = message.chat.id
    
    if chat_id in active_chats:
        await message.reply("✅ Auto-approve is already active here")
        return
    
    # Verify permissions
    try:
        me = await ubot.get_chat_member(chat_id, "me")
        if not me.privileges.can_invite_users:
            await message.reply("❌ I need 'Invite Users' permission!")
            return
    except Exception as e:
        await message.reply(f"❌ Permission check failed: {str(e)}")
        return
    
    active_chats[chat_id] = True
    asyncio.create_task(process_pending_requests(chat_id))
    
    await message.reply("🚀 Auto-approve activated!\n"
                      "• Processing pending requests...\n"
                      "• New requests will auto-approve")

@ubot.on_message(filters.command("stopapprove") & filters.user(OWNER_IDS))
async def disable_auto_approve(_, message: Message):
    chat_id = message.chat.id
    
    if chat_id not in active_chats:
        await message.reply("ℹ️ Auto-approve isn't active here")
        return
    
    active_chats.pop(chat_id)
    await message.reply("⛔ Auto-approve deactivated")

@ubot.on_chat_join_request()
async def handle_new_request(_, request: ChatJoinRequest):
    if request.chat.id in active_chats:
        try:
            await ubot.approve_chat_join_request(request.chat.id, request.from_user.id)
            logger.info(f"Auto-approved {request.from_user.id}")
        except FloodWait as e:
            logger.warning(f"FloodWait: Sleeping {e.value}s")
            await asyncio.sleep(e.value)
        except Exception as e:
            logger.error(f"Approval error: {str(e)}")
