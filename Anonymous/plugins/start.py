# (©) Anonymous Emperor 

from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.types import InlineKeyboardButton as Anonymous
from Anonymous import app
from Anonymous.config import Config
import random
from pymongo import MongoClient

# MongoDB URI and Client
MONGO_URI = Config.MONGO_URI  # Add your MongoDB URI in Config
mongo_client = MongoClient(MONGO_URI)
db = mongo_client["AnonymousDB"]  # Replace with your database name
USERS_COLLECTION = db["users"]
CHATS_COLLECTION = db["chats"]

C_HANDLER = ["/", "!", "?", "."]

@app.on_message(filters.command(["start"]), group=89898979)
async def start(client, message):
    """Start command to display bot details."""
    random_image = random.choice([
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
    ])
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Add me to your group/channel", url="http://t.me/Toji_ProXBot?startgroup=true")],
        [InlineKeyboardButton("Help", callback_data="main_help"), InlineKeyboardButton("Support", url="https://t.me/Raiden_Support")]
    ])
    
    await client.send_photo(
        chat_id=message.chat.id,
        photo=random_image,
        caption="• Hello ㅤ!\n• I'm The Toji • Fushiguro, And I'm Here To SafeGuard🛡️ Your Group.",
        reply_markup=keyboard
    )


   
@app.on_message(filters.command(["botstart"], C_HANDLER) & filters.private)
async def help(client, message):
    """Start command to display bot details."""
    random_image = random.choice([
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
    ])
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Add me to your group/channel", url="http://t.me/Toji_ProXBot?startgroup=true")],
        [InlineKeyboardButton("Help", callback_data="main_help"), InlineKeyboardButton("Support", url="https://t.me/Raiden_Support")]
    ])
    
    await client.send_photo(
        chat_id=message.chat.id,
        photo=random_image,
        caption="• Hello ㅤ!\n• I'm The Edit Deleter Bot, And I'm Here To SafeGuard🛡️ Your Group.",
        reply_markup=keyboard
    )



@app.on_message(filters.command(["help"])  & filters.group, group=696969969)
async def group_help(client, message: Message):
    """Handles the /help command in groups."""
    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton("Help and Commands", url=f"t.me/{app.me.username}?start=help")]]
    )
    await message.reply_text(
 #       "🛡 **Help Menu** 🛡\n\n"
        "𝖢𝗅𝗂𝖼𝗄 𝖮𝗇 𝖳𝗁𝖾 𝖡𝗎𝗍𝗍𝗈𝗇 𝖡𝖾𝗅𝗈𝗐 𝖳𝗈 𝖦𝖾𝗍 𝖬𝗒 𝖧𝖾𝗅𝗉 𝖬𝖾𝗇𝗎 𝖨𝗇 𝖸𝗈𝗎𝗋 𝖯𝗆.",
        reply_markup=keyboard
    )

async def send_main_help(client, message):
    """Send main help menu."""
    random_image = random.choice([
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
    ])
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Admin Commands", callback_data="help_admin"),
        InlineKeyboardButton("Bans Commands", callback_data="help_ban")],
        [Anonymous("Imposter Commands", callback_data="help_imposter"),
        InlineKeyboardButton("Protection Features", callback_data="help_protection")],
        [InlineKeyboardButton("UserBot Protection", callback_data="help_userbot"),
         Anonymous("Games", callback_data="help_game")],
        [InlineKeyboardButton("Anime Channel", url="https://t.me/Weeb_TV")],
        [Anonymous("Close", callback_data="close_info")]
    ])
    await client.send_photo(
        chat_id=message.chat.id,
        photo=random_image,
        caption="**• Help Menu •**\n\nClick the buttons below to explore specific sections.",
        reply_markup=keyboard
    )

@app.on_message(filters.command(["help"]) & filters.private)
async def help(client, message: Message):
    """Start command to display main help menu in private."""
    await send_main_help(client, message)



@app.on_callback_query(filters.regex("main_help"))
async def callback_main_help(client, callback_query: CallbackQuery):
    """Handle main help callback."""
    await callback_query.answer()
    await callback_query.message.edit_text(
       "**• Help Menu •**\n\nClick the buttons below to explore specific sections.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Admin Commands", callback_data="help_admin"),
            InlineKeyboardButton("Bans Commands", callback_data="help_ban")],
            [Anonymous("Imposter Commands", callback_data="help_imposter"),
            InlineKeyboardButton("Protection Features", callback_data="help_protection")],
            [InlineKeyboardButton("UserBot Protection", callback_data="help_userbot"),
             Anonymous("Games", callback_data="help_game")],
            #[Anonymous("UserBot Protection", callback_data="help_userbot"),
            [InlineKeyboardButton("Anime Channel", url="https://t.me/Weeb_TV")],
            [Anonymous("Close", callback_data="close_info")]
        ])
    )


@app.on_callback_query(filters.regex("help_admin"))
async def help_admin(client, callback_query: CallbackQuery):
    """Admin commands help."""
    help_text = """
**• Admin Commands:**

1. **/ban [user] [reason (optional)]** - Bans a user from the chat. Usage: Reply: `/ban [reason]` or Username/ID: `/ban @username` or `/ban 123456789`\n
2. **/unban [user]** - Unbans a user from the chat. Usage: Reply: `/unban` or Username/ID: `/unban @username` or `/unban 123456789`\n
3. **/mute [user] [reason (optional)]** - Mutes a user indefinitely in the chat. Usage: Reply: `/mute [reason]` or Username/ID: `/mute @username` or `/mute 123456789`\n
4. **/unmute [user]** - Unmutes a user in the chat. Usage: Reply: `/unmute` or Username/ID: `/unmute @username` or `/unmute 123456789`\n
5. **/tmute [user] [duration] [reason (optional)]** - Temporarily mutes a user for the specified duration. Usage: Reply: `/tmute 10m [reason]` or Username/ID: `/tmute @username 1h` or `/tmute 123456789 2d`\n

**Note:** These commands can only be used by Admins or Owners. Always ensure the bot has the required permissions (e.g., `Ban Members`, `Restrict Members`).
    """
    await callback_query.answer()
    await callback_query.message.edit_text(help_text, reply_markup=InlineKeyboardMarkup([
        [InlineKeyboardButton("« Back", callback_data="main_help")]
    ]))

@app.on_callback_query(filters.regex("help_game"))
async def help_game(client, callback_query: CallbackQuery):
    """Game commands help."""
    help_text = (
        "**🎮 Toji • Fushiguro Game Commands:**\n\n"
        "1. **Game Controls**\n"
        "   - `/new` - Start a new word guessing game\n"
        "   - `/end` - End current game\n"
        "   - `/hint [position]` - Get hint for a letter position (costs 1 point)\n\n"
        "2. **Word Management (Admins Only)**\n"
        "   - `/addword [word]` - Add word to dictionary\n"
        "   - `/delword [word]` - Remove word from dictionary\n"
        "   - `/checkword [word]` - Check if word exists\n\n"
        "3. **Leaderboards**\n"
        "   - `/leaderboard` - View top players\n"
 #       "   - `/stats` - View bot statistics (Admin only)\n\n"
        "4. **Admin Tools**\n"
        "   - `/broadcast [message]` - Broadcast message to all users\n"
        "   - `/check` - Reveal current game's word (Admin only)\n\n"
        "**Game Rules:**\n"
        "- Guess words of selected length (3-7 letters)\n"
        "- 🟩 = Correct letter & position\n"
        "- 🟨 = Correct letter, wrong position\n"
        "- 🟥 = Letter not in word\n"
        "- Earn points for correct guesses"
    )
    await callback_query.answer()
    await callback_query.message.edit_text(
        help_text,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("« Back", callback_data="main_help")]
        ])
    )


@app.on_callback_query(filters.regex("help_ban"))
async def help_ban(client, callback_query: CallbackQuery):
    """Ban commands help."""
    help_text = """
**• Ban Commands:**

1. **/ban [user] [reason (optional)]** - Bans a user from the chat. Usage: Reply: `/ban [reason]` or Username/ID: `/ban @username` or `/ban 123456789`\n
2. **/unban [user]** - Unbans a user from the chat. Usage: Reply: `/unban` or Username/ID: `/unban @username` or `/unban 123456789`\n
3. **/mute [user] [reason (optional)]** - Mutes a user indefinitely in the chat. Usage: Reply: `/mute [reason]` or Username/ID: `/mute @username` or `/mute 123456789`\n
4. **/unmute [user]** - Unmutes a user in the chat. Usage: Reply: `/unmute` or Username/ID: `/unmute @username` or `/unmute 123456789`\n
5. **/tmute [user] [duration] [reason (optional)]** - Temporarily mutes a user for the specified duration. Usage: Reply: `/tmute 10m [reason]` or Username/ID: `/tmute @username 1h` or `/tmute 123456789 2d`\n\n

**Note:** These commands can only be used by Admins or Owners. Always ensure the bot has the required permissions (e.g., `Ban Members`, `Restrict Members`).
    """
    await callback_query.answer()
    await callback_query.message.edit_text(help_text, reply_markup=InlineKeyboardMarkup([
        [InlineKeyboardButton("« Back", callback_data="main_help")]
    ]))

@app.on_callback_query(filters.regex("help_protection"))
async def help_protection(client, callback_query: CallbackQuery):
    """Protection features help."""
    help_text = (
        "**• Protection Features:**\n\n"
        "1. **Edited Message Deleter** - Deletes edited messages automatically.\n"
        "2. **Exceptions** - Use `/permit` to allow specific users to edit messages without deletion.\n\n"
        "3. **Auto-Delete Images**\n"
        "   - `/setdelay [time]` - Auto-delete images after specified time (e.g. 30s, 5m, 1h)\n"
        "   - `/disableimgdelete` - Disable auto-delete for images\n\n"
        "4. **Abuse Management Commands**\n"
        "   - `/addabuse [word]` - Add an abusive word for this group.\n"
        "   - `/deleteabuse [word]` - Remove an abusive word from this group.\n"
        "   - `/abuselist` - View the list of abusive words for this group.\n\n"
        "5. **Link Management Commands**\n"
        "   - `/addlink [link]` - Add a permitted link for this group.\n"
        "   - `/deletelink [link]` - Remove a permitted link from this group.\n"
        "   - `/linklist` - View the list of permitted links for this group.\n\n"
        "**Time Units:** s=seconds, m=minutes, h=hours, d=days"
    )
    await callback_query.answer()
    await callback_query.message.edit_text(
        help_text,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("« Back", callback_data="main_help")]
        ])
    )

@app.on_callback_query(filters.regex("help_userbot"))
async def help_autodelete(client, callback_query: CallbackQuery):
    """Auto-delete commands help."""
    help_text = """
**• Auto-Delete Commands:**

1. `/autodelete <time><unit> [media]`  
   - Delete media after time (eg: `30m` or `2h photo video`)  
   - Units: s/m/h/d | Media: photo/video/sticker/gif/doc  

2. `/stopautodelete` - Stop media deletion  

3. `/setdelete <time><unit>`  
   - Delete ALL msgs periodically (eg: `1h`)  

4. `/stopdelete` - Stop periodic deletion  

5. `/join <link>`  
   - Add UserBot to chat  

**Notes:**  
- Needs admin/owner rights  
- UserBot requires delete permissions  
- Large chats may take time  
- Runs continuously (media) or on interval (all)  
"""
    await callback_query.answer()
    await callback_query.message.edit_text(
        help_text,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("« Back", callback_data="main_help")]
        ])
    )

#@app.on_callback_query(filters.regex("help_userbot"))
async def help_delete(client, callback_query: CallbackQuery):
    """Auto-delete commands help."""
    help_text = """
**• Auto-Delete Commands:**

1. **/autodelete <time><unit> [media types]**  
   - Enables automatic deletion of media messages after specified time  
   - Example: `/autodelete 30m` (deletes all media after 30 minutes)  
   - Example: `/autodelete 2h photo video` (deletes only photos/videos after 2 hours)  
   - Units: `s` (seconds), `m` (minutes), `h` (hours), `d` (days)  
   - Media types: `photo`, `video`, `sticker`, `gif`, `document`  

2. **/stopautodelete**  
   - Stops the automatic media deletion in current chat  

3. **/setdelete <time><unit>**  
   - Sets periodic deletion of ALL messages in the chat  
   - Example: `/setdelete 1h` (deletes ALL messages every hour)  
   - Example: `/setdelete 30m` (clears chat every 30 minutes)  

4. **/stopdelete**  
   - Stops the periodic message deletion  

5. **/inviteubot**  
   - Manually invites the UserBot to the chat (required for auto-delete to work)  

6. **/join <link>**  
   - Makes the UserBot join the current chat of provided link

**Notes:**  
- These commands require admin/owner privileges  
- The UserBot needs delete permissions  
- For large chats, deletion may take time  
- Media deletion runs continuously (checks every minute)  
- Full chat deletion runs on the specified interval  
    """
    await callback_query.answer()
    await callback_query.message.edit_text(
        help_text,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("« Back", callback_data="main_help")]
        ])
    )
@app.on_callback_query(filters.regex("help_purge"))
async def help_purge(client, callback_query: CallbackQuery):
    """Purge commands help."""
    help_text = """
**• Purge Commands:**

1. **/purge** - Deletes all messages between the replied-to message and the command message.\n
2. **/spurge** - Same as /purge, but for specific cases.\n
3. **/del** - Deletes the replied-to message.\n
    """
    await callback_query.answer()
    await callback_query.message.edit_text(help_text, reply_markup=InlineKeyboardMarkup([
        [InlineKeyboardButton("« Back", callback_data="main_help")]
    ]))

@app.on_callback_query(filters.regex("help_imposter"))
async def help_imposter(client, callback_query:CallbackQuery):
    """Imposter commands help"""
    help_text = (
    "**ᴘʀᴇᴛᴇɴᴅᴇʀ ᴅᴇᴛᴇᴄᴛɪᴏɴ ᴍᴏᴅᴜʟᴇ**\n\n"
    "This module tracks and logs changes made to users' **username**, **first name**, and **last name** in a group. "
    "It helps to detect imposters by logging any modifications to a user's profile.\n\n"
    "**🔹 ᴄᴏᴍᴍᴀɴᴅs ᴀɴᴅ ᴜsᴀɢᴇ:**\n\n"
    "1. **Enable Pretender Detection**\n"
    "   **Command:** `/imposter on or enable`\n"
    "   Enables the pretender detection mode for the group. The bot will monitor and log any changes made to users' profile details.\n\n"
    "2. **Disable Pretender Detection**\n"
    "   **Command:** `/imposter off or disable`\n"
    "   Disables the pretender detection mode for the group. No changes will be monitored or logged.\n\n"
    "3. **Check Status**\n"
    "   **Command:** `/imposter`\n"
    "   Use this command without arguments to get usage instructions.\n"
    )
    await callback_query.answer()
    await callback_query.message.edit_text(help_text, reply_markup=InlineKeyboardMarkup([
        [InlineKeyboardButton("« Back", callback_data="main_help")]
    ]))

@app.on_callback_query(filters.regex(pattern=r"close_info"))
async def close_info_button(c: app, callback_query: CallbackQuery):
    await callback_query.answer()
    await callback_query.message.delete()


