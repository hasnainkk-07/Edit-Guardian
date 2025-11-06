from pyrogram import enums
from pyrogram.types import Message
from Anonymous import app
from Anonymous.filters import command
from Anonymous.database.users_db import Users
from Anonymous.database.chats_db import Chats
from hydragram import handler

#@app.on_message(command(["stats"], dev_cmd=True))
@handler("stats", dev_cmd=True)
async def get_stats(_, m: Message):
    replymsg = await m.reply_text("<b><i>Fetching Stats...</i></b>", quote=True)

    user_count = Users.count_users()
    chat_count = Chats.count_chats()

    await replymsg.edit_text(
        f"📊 𝗕𝗢𝗧 𝗦𝗧𝗔𝗧𝗜𝗦𝗧𝗜𝗖𝗦 📊\n\n"
        f"<b>👥 Users:</b> <code>{user_count}</code>\n"
        f"<b>💬 Chats:</b> <code>{chat_count}</code>\n\n"
        "<a href='https://t.me/Infamous_News'>𝙐𝙋𝘿𝘼𝙏𝙀𝙎</a> | "
        "<a href='https://t.me/Raiden_Support'>𝙎𝙐𝙋𝙋𝙊𝙍𝙏</a>\n\n"
        "「 𝙈𝘼𝘿𝙀 𝘽𝙔 <a href='https://t.me/Anonymous_Emperor'>𝖠𝗇𝗈𝗇𝗒𝗆𝗈𝗎𝗌 𝖤𝗆𝗉𝖾𝗋𝗈𝗋</a> 」",
        parse_mode=enums.ParseMode.HTML,
        disable_web_page_preview=True
    )
