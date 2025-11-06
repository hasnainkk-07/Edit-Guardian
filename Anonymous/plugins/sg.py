import asyncio
import random

from pyrogram import Client
from pyrogram.types import Message
from pyrogram.raw.functions.messages import DeleteHistory

from Anonymous import ubot as us, app, filters  # `us` is your userbot client


@app.on_message(filters.command("sg") & (filters.private | filters.group))
async def sg(client: Client, message: Message):
    if len(message.text.split()) < 2 and not message.reply_to_message:
        return await message.reply("Reply to a user or provide a username/id.\n\nUsage: `/sg @username`", quote=True)
    
    # Get target user ID or username
    if message.reply_to_message:
        target = message.reply_to_message.from_user.id
    else:
        target = message.text.split()[1]
    
    status_msg = await message.reply("<code>Processing...</code>")
    
    try:
        user = await client.get_users(target)
    except Exception:
        return await status_msg.edit("<code>Invalid user. Please try again.</code>")
    
    sangmata_bot = random.choice(["sangmata_bot", "sangmata_beta_bot"])

    try:
        sent = await us.send_message(sangmata_bot, str(user.id))
        await sent.delete()
    except Exception as e:
        return await status_msg.edit(f"<code>{e}</code>")
    
    await asyncio.sleep(1)
    
    async for msg in us.search_messages(sangmata_bot):
        if not msg or not msg.text:
            continue
        await message.reply(msg.text)
        break
    
    try:
        peer = await us.resolve_peer(sangmata_bot)
        await us.send(DeleteHistory(peer=peer, max_id=0, revoke=True))
    except Exception:
        pass

    await status_msg.delete()
