# (©) Anonymous Emperor 

from Anonymous import filters
from pyrogram.types import Message

from Anonymous import app
from Anonymous.config import SUDOERS, Config
from Anonymous.database.sudo import add_sudo, remove_sudo
from Anonymous.helpers.extraction import extract_user


OWNER_ID = Config.OWNER_ID


@app.on_message(filters.command(["addsudo"], dev_cmd=True)) # & filters.user(OWNER_ID), group=899898989)
async def useradd(client, message: Message):
    if not message.reply_to_message:
        if len(message.command) != 2:
            return await message.reply_text("𝖱𝖾𝗉𝗅𝗒 𝖳𝗈 𝖠 𝖴𝗌𝖾𝗋'𝗌 𝖬𝖾𝗌𝗌𝖺𝗀𝖾 𝖮𝗋 𝖦𝗂𝗏𝖾 𝖴𝗌𝖾𝗋𝗇𝖺𝗆𝖾 / 𝖴𝗌𝖾𝗋 𝖨𝖣 .")
    user = await extract_user(message)
    if user.id in SUDOERS:
        return await message.reply_text(f"» {user.mention} 𝖨𝗌 𝖠𝗅𝗋𝖾𝖺𝖽𝗒 𝖨𝗇 𝖲𝗎𝖽𝗈 𝖴𝗌𝖾𝗋 𝖫𝗂𝗌𝗍 .")
    added = await add_sudo(user.id)
    if added:
        SUDOERS.add(user.id)
        await message.reply_text(f"» 𝖠𝖽𝖽𝖾𝖽 {user.mention} 𝖳𝗈 𝖲𝗎𝖽𝗈 𝖴𝗌𝖾𝗋 𝖫𝗂𝗌𝗍 .")
    else:
        await message.reply_text("𝖥𝖺𝗂𝗅𝖾𝖽 .")


@app.on_message(filters.command(["delsudo", "rmsudo"], dev_cmd=True)) # & filters.user(OWNER_ID), group=8989898989)
async def userdel(client, message: Message):
    if not message.reply_to_message:
        if len(message.command) != 2:
            return await message.reply_text("𝖱𝖾𝗉𝗅𝗒 𝖳𝗈 𝖠 𝖴𝗌𝖾𝗋'𝗌 𝖬𝖾𝗌𝗌𝖺𝗀𝖾 𝖮𝗋 𝖦𝗂𝗏𝖾 𝖴𝗌𝖾𝗋𝗇𝖺𝗆𝖾 / 𝖴𝗌𝖾𝗋 𝖨𝖣 .")
    user = await extract_user(message)
    if user.id not in SUDOERS:
        return await message.reply_text(f"» {user.mention} 𝖨𝗌 𝖭𝗈𝗍 𝖨𝗇 𝖲𝗎𝖽𝗈 𝖴𝗌𝖾𝗋𝗌 𝖫𝗂𝗌𝗍 .")
    removed = await remove_sudo(user.id)
    if removed:
        SUDOERS.remove(user.id)
        await message.reply_text(f"» 𝖱𝖾𝗆𝗈𝗏𝖾𝖽 {user.mention} 𝖥𝗋𝗈𝗆 𝖲𝗎𝖽𝗈 𝖴𝗌𝖾𝗋 𝖫𝗂𝗌𝗍 .")
    else:
        await message.reply_text("𝖥𝖺𝗂𝗅𝖾𝖽 .")



@app.on_message(filters.command(["sudolist", "listsudo", "sudoers"], dev_cmd=True))
async def sudoers_list(client, message: Message):
    text = "<u><b>💀 𝖮𝗐𝗇𝖾𝗋 🐐 :</b></u>\n"

    try:
        owner = await app.get_users(OWNER_ID)
        owner_mention = owner.mention if hasattr(owner, "mention") else owner.first_name
        text += f"1➤ {owner_mention}\n"
    except:
        text += "1➤ Owner not found\n"

    smex = 0
    count = 2  # Since owner is 1

    # Loop through SUDOERS (if any) excluding owner
    for user_id in SUDOERS:
        if user_id == OWNER_ID:
            continue
        try:
            sudo_user = await app.get_users(user_id)
            sudo_mention = sudo_user.mention if hasattr(sudo_user, "mention") else sudo_user.first_name
            if smex == 0:
                smex += 1
                text += "\n<u><b>✨ 𝖲𝗎𝖽𝗈 𝖴𝗌𝖾𝗋 ✨:</b></u>\n"
            text += f"{count}➤ {sudo_mention}\n"
            count += 1
        except:
            continue

    if count == 2:  # No sudo users
        await message.reply_text("» 𝖭𝗈 𝖲𝗎𝖽𝗈 𝖴𝗌𝖾𝗋𝗌 𝖥𝗈𝗎𝗇𝖽.")
    else:
        await message.reply_text(text)
