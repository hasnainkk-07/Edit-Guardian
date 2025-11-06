import logging
from pyrogram import filters
from pyrogram.enums import ParseMode, ChatType
from pyrogram.types import ChatMemberUpdated
from Anonymous import app, ubot
from Anonymous.config import Config # Your logging channel
LOGS = Config.LOGS

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def is_admin(chat_id: int, user_id: int) -> bool:
    """Check if user is admin in the chat"""
    try:
        member = await app.get_chat_member(chat_id, user_id)
        return member.privileges.can_invite_users if member.privileges else False
    except Exception as e:
        logger.error(f"Error checking admin status: {e}")
        return False

@app.on_chat_member_updated()
async def auto_add_userbot(client, chat_member: ChatMemberUpdated):
    try:
        # Check if the bot was added to a group
        if (chat_member.new_chat_member and
            chat_member.new_chat_member.user.id == app.me.id and
            chat_member.new_chat_member.status == "member" and
            chat_member.chat.type in [ChatType.GROUP, ChatType.SUPERGROUP]):
            
            chat_id = chat_member.chat.id
            chat_title = chat_member.chat.title
            
            # Check if bot has admin privileges to add users
            if not await is_admin(chat_id, app.me.id):
                logger.warning(f"Bot not admin in {chat_title} (ID: {chat_id})")
                await app.send_message(
                    LOGS,
                    f"⚠️ **Bot Added But Not Admin**\n\n"
                    f"**Group:** {chat_title}\n"
                    f"**ID:** `{chat_id}`\n\n"
                    f"Cannot auto-add userbot without admin rights.",
                    parse_mode=ParseMode.MARKDOWN
                )
                return
            
            # Check if userbot is already in the group
            try:
                member = await ubot.get_chat_member(chat_id, ubot.me.id)
                if member.status in ["member", "administrator", "creator"]:
                    logger.info(f"Userbot already in {chat_title} (ID: {chat_id})")
                    return
            except Exception as e:
                logger.info(f"Userbot not in {chat_title} (ID: {chat_id}), adding now...")
            
            # Add userbot to the group
            try:
                # Method 1: Try adding directly
                await app.add_chat_members(chat_id, ubot.me.username)
                logger.info(f"Successfully added userbot to {chat_title} (ID: {chat_id})")
                
                # Send success notification
                await app.send_message(
                    LOGS,
                    f"✅ **Auto-Added Userbot**\n\n"
                    f"**Group:** {chat_title}\n"
                    f"**ID:** `{chat_id}`\n\n"
                    f"Userbot successfully added to the group!",
                    parse_mode=ParseMode.MARKDOWN
                )
                
            except Exception as add_error:
                logger.warning(f"Direct add failed, trying invite link: {add_error}")
                
                # Method 2: Fallback to invite link
                try:
                    invite_link = await app.export_chat_invite_link(chat_id)
                    await ubot.join_chat(invite_link)
                    logger.info(f"Added userbot via invite link to {chat_title}")
                    
                    await app.send_message(
                        LOGS,
                        f"✅ **Auto-Added Userbot via Invite Link**\n\n"
                        f"**Group:** {chat_title}\n"
                        f"**ID:** `{chat_id}`",
                        parse_mode=ParseMode.MARKDOWN
                    )
                    
                except Exception as invite_error:
                    error_msg = (
                        f"❌ **Failed to Add Userbot**\n\n"
                        f"**Group:** {chat_title}\n"
                        f"**ID:** `{chat_id}`\n\n"
                        f"**Errors:**\n"
                        f"- Direct add: `{add_error}`\n"
                        f"- Invite link: `{invite_error}`"
                    )
                    await app.send_message(LOGS, error_msg, parse_mode=ParseMode.MARKDOWN)
                    logger.error(f"Failed to add userbot to {chat_id}: {add_error} | {invite_error}")
                    
    except Exception as e:
        logger.critical(f"Unexpected error in auto_add_userbot: {e}", exc_info=True)
        await app.send_message(
            LOGS,
            f"🚨 **Critical Error in Auto-Add**\n\n"
            f"```python\n{e}\n```",
            parse_mode=ParseMode.MARKDOWN
        )
