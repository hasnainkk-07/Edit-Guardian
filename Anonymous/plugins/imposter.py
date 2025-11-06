# (©) Anonymous Emperor 

import random 
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from Anonymous.database.imposter import impo_off, impo_on, check_pretender, add_userdata, get_userdata, usr_data
from Anonymous import app
from Anonymous.helpers.filters import admin_filter as admin, bot_owner_filter as owner


Anonymous_Img = [
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


Anonymous = [
    [
        InlineKeyboardButton(
            text="ᴀᴅᴅ ᴍᴇ",
            url=f"https://t.me/Toji_ProXBot?startgroup=true"),
        InlineKeyboardButton(text="ᴜᴘᴅᴀᴛᴇ", url=f"https://t.me/Infamous_News")
    ],
]


@app.on_message(filters.group & ~filters.bot & ~filters.via_bot, group=696969)
async def chk_usr(_, message: Message):
    if message.sender_chat or not await check_pretender(message.chat.id):
        return
    if not await usr_data(message.from_user.id):
        return await add_userdata(
            message.from_user.id,
            message.from_user.username,
            message.from_user.first_name,
            message.from_user.last_name,
        )
    usernamebefore, first_name, lastname_before = await get_userdata(message.from_user.id)
    msg = ""
    if (
        usernamebefore != message.from_user.username
        or first_name != message.from_user.first_name
        or lastname_before != message.from_user.last_name
    ):
        msg += f"""
**ᴜsᴇʀ sʜᴏʀᴛ ɪɴғᴏʀᴍᴀᴛɪᴏɴ**

**๏ ɴᴀᴍᴇ** ➛ {message.from_user.mention}
**๏ ᴜsᴇʀ ɪᴅ** ➛ {message.from_user.id}
"""
    if usernamebefore != message.from_user.username:
        usernamebefore = f"@{usernamebefore}" if usernamebefore else "NO USERNAME"
        usernameafter = (
            f"@{message.from_user.username}"
            if message.from_user.username
            else "NO USERNAME"
        )
        msg += """
**ᴄʜᴀɴɢᴇᴅ ᴜsᴇʀɴᴀᴍᴇ**

**๏ ʙᴇғᴏʀᴇ** ➛ {bef}
**๏ ᴀғᴛᴇʀ** ➛ {aft}
""".format(bef=usernamebefore, aft=usernameafter)
        await add_userdata(
            message.from_user.id,
            message.from_user.username,
            message.from_user.first_name,
            message.from_user.last_name,
        )
    if first_name != message.from_user.first_name:
        msg += """
**ᴄʜᴀɴɢᴇs ғɪʀsᴛ ɴᴀᴍᴇ**

**๏ ʙᴇғᴏʀᴇ** ➛ {bef}
**๏ ᴀғᴛᴇʀ** ➛ {aft}
""".format(
            bef=first_name, aft=message.from_user.first_name
        )
        await add_userdata(
            message.from_user.id,
            message.from_user.username,
            message.from_user.first_name,
            message.from_user.last_name,
        )
    if lastname_before != message.from_user.last_name:
        lastname_before = lastname_before or "NO LAST NAME"
        lastname_after = message.from_user.last_name or "NO LAST NAME"
        msg += """
**ᴄʜᴀɴɢᴇs ʟᴀsᴛ ɴᴀᴍᴇ**

**๏ ʙᴇғᴏʀᴇ** ➛ {bef}
**๏ ᴀғᴛᴇʀ** ➛ {aft}
""".format(
            bef=lastname_before, aft=lastname_after
        )
        await add_userdata(
            message.from_user.id,
            message.from_user.username,
            message.from_user.first_name,
            message.from_user.last_name,
        )
    if msg != "":
        await message.reply_photo(random.choice(Anonymous_Img), caption=msg, reply_markup=InlineKeyboardMarkup(Anonymous),)

@app.on_message(filters.group & filters.command("imposter") & ~filters.bot & ~filters.via_bot & (admin | owner), group=6969669)
async def set_mataa(_, message: Message):
    if len(message.command) == 1:
        return await message.reply("**ᴅᴇᴛᴇᴄᴛ ᴘʀᴇᴛᴇɴᴅᴇʀ ᴜsᴇʀs ᴜsᴀɢᴇ : ᴘʀᴇᴛᴇɴᴅᴇʀ ᴏɴ|ᴏғғ**")
    
    command = message.command[1].lower()  # Convert to lowercase for consistency
    if command in ["enable", "on"]:
        cekset = await impo_on(message.chat.id)
        if cekset:
            await message.reply("**ᴘʀᴇᴛᴇɴᴅᴇʀ ᴍᴏᴅᴇ ɪs ᴀʟʀᴇᴀᴅʏ ᴇɴᴀʙʟᴇᴅ.**")
        else:
            await impo_on(message.chat.id)
            await message.reply(f"**sᴜᴄᴄᴇssғᴜʟʟʏ ᴇɴᴀʙʟᴇᴅ ᴘʀᴇᴛᴇɴᴅᴇʀ ᴍᴏᴅᴇ ғᴏʀ** {message.chat.title}")
    elif command in ["disable", "off"]:
        cekset = await impo_off(message.chat.id)
        if not cekset:
            await message.reply("**ᴘʀᴇᴛᴇɴᴅᴇʀ ᴍᴏᴅᴇ ɪs ᴀʟʀᴇᴀᴅʏ ᴅɪsᴀʙʟᴇᴅ.**")
        else:
            await impo_off(message.chat.id)
            await message.reply(f"**sᴜᴄᴄᴇssғᴜʟʟʏ ᴅɪsᴀʙʟᴇᴅ ᴘʀᴇᴛᴇɴᴅᴇʀ ᴍᴏᴅᴇ ғᴏʀ** {message.chat.title}")
    else:
        await message.reply("**ᴅᴇᴛᴇᴄᴛ ᴘʀᴇᴛᴇɴᴅᴇʀ ᴜsᴇʀs ᴜsᴀɢᴇ : ᴘʀᴇᴛᴇɴᴅᴇʀ ᴏɴ|ᴏғғ**")
