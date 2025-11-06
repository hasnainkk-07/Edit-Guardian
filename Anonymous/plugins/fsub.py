from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from pyrogram.errors import ChatAdminRequired, UserNotParticipant, ChatWriteForbidden
from Anonymous import app

# Configurable settings
MUST_JOIN = "Weeb_Tv"  # Main channel/group username or ID
ALT_JOIN = "Infamous_News" # Alternative channel/group (optional)
WELCOME_IMAGE = "https://files.catbox.moe/ioygr1.jpg"  # Default image
MESSAGE = """
๏ ᴀᴄᴄᴏʀᴅɪɴɢ ᴛᴏ ᴍʏ ᴅᴀᴛᴀʙᴀsᴇ ʏᴏᴜ'ᴠᴇ ɴᴏᴛ ᴊᴏɪɴᴇᴅ [๏sᴜᴘᴘᴏʀᴛ๏]({link}) ʏᴇᴛ!

ɪғ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ᴜsᴇ ᴍᴇ:
1. ᴊᴏɪɴ ᴏᴜʀ ᴄʜᴀɴɴᴇʟ
2. ᴛʀʏ ᴀɢᴀɪɴ ᴀғᴛᴇʀ ᴊᴏɪɴɪɴɢ
"""

@app.on_message(filters.incoming & filters.private, group=-1)
async def force_subscribe(app: Client, msg: Message):
    if not MUST_JOIN:
        return
        
    try:
        try:
            await app.get_chat_member(MUST_JOIN, msg.from_user.id)
            # Check alternative channel if set
            if ALT_JOIN:
                await app.get_chat_member(ALT_JOIN, msg.from_user.id)
            return
        except UserNotParticipant:
            # Generate invite link
            chat_info = await app.get_chat(MUST_JOIN)
            link = chat_info.invite_link if not MUST_JOIN.isalpha() else f"https://t.me/{MUST_JOIN}"
            
            # Prepare buttons
            buttons = [[InlineKeyboardButton("๏Jᴏɪɴ Mᴀɪɴ Cʜᴀɴɴᴇʟ๏", url=link)]]
            
            if ALT_JOIN:
                alt_link = (await app.get_chat(ALT_JOIN)).invite_link if not ALT_JOIN.isalpha() else f"https://t.me/{ALT_JOIN}"
                buttons.append([InlineKeyboardButton("๏Jᴏɪɴ Aʟᴛ Cʜᴀɴɴᴇʟ๏", url=alt_link)])
            
            buttons.append([InlineKeyboardButton("๏Tʀʏ Aɢᴀɪɴ๏", url=f"https://t.me/{app.me.username}?start=check")])
            
            try:
                await msg.reply_photo(
                    photo=WELCOME_IMAGE,
                    caption=MESSAGE.format(link=link),
                    reply_markup=InlineKeyboardMarkup(buttons),
                    disable_web_page_preview=True
                )
                await msg.stop_propagation()
            except ChatWriteForbidden:
                pass
    except ChatAdminRequired:
        print(f"⚠️ Please promote me as admin in {MUST_JOIN} with invite users permission!")

# Additional handler for group messages (if needed)
@app.on_message(filters.incoming & filters.group, group=-1)
async def group_force_sub(app: Client, msg: Message):
    if not MUST_JOIN:
        return
        
    try:
        await app.get_chat_member(MUST_JOIN, msg.from_user.id)
        if ALT_JOIN:
            await app.get_chat_member(ALT_JOIN, msg.from_user.id)
    except UserNotParticipant:
        try:
           # await msg.delete()
            chat_info = await app.get_chat(MUST_JOIN)
            link = chat_info.invite_link if not MUST_JOIN.isalpha() else f"https://t.me/{MUST_JOIN}"
            
            sent = await app.send_message(
                msg.from_user.id,
                text=MESSAGE.format(link=link),
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("๏ Jᴏɪɴ Cʜᴀɴɴᴇʟ ๏", url=link)],
                    [InlineKeyboardButton("๏ Tʀʏ Aɢᴀɪɴ ๏", url=f"t.me/{app.me.username}?start=check")]
                ])
            )
            
            if ALT_JOIN:
                alt_link = (await app.get_chat(ALT_JOIN)).invite_link if not ALT_JOIN.isalpha() else f"https://t.me/{ALT_JOIN}"
                await sent.edit_reply_markup(
                    InlineKeyboardMarkup([
                        [InlineKeyboardButton("๏ Jᴏɪɴ Mᴀɪɴ Cʜᴀɴɴᴇʟ ๏", url=link)],
                        [InlineKeyboardButton("๏ Jᴏɪɴ Aʟᴛ Cʜᴀɴɴᴇʟ ๏", url=alt_link)],
                        [InlineKeyboardButton("๏ Tʀʏ Aɢᴀɪɴ ๏", url=f"t.me/{app.me.username}?start=check")]
                    ])
                )
        except Exception as e:
            print(f"Force sub error: {e}")
