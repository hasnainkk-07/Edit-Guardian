import os
import shutil
from pyrogram import filters, Client
from Anonymous import app, ubot
from Anonymous.config import Config as ap
from Anonymous.helpers.filters import bot_owner_filter as owner

@ubot.on_message(filters.command(["restart"]) & owner, group=898989898979)
async def restart_(_, message):
    response = await message.reply_text("ʀᴇsᴛᴀʀᴛɪɴɢ...")
    
    # Cleanup temporary directories
    try:
        shutil.rmtree("downloads")
        shutil.rmtree("raw_files")
        shutil.rmtree("cache")
    except:
        pass
    
    await response.edit_text(
        "» ʀᴇsᴛᴀʀᴛ ᴘʀᴏᴄᴇss sᴛᴀʀᴛᴇᴅ, ᴘʟᴇᴀsᴇ Wᴀɪᴛ ғᴏʀ ғᴇᴡ sᴇᴄᴏɴᴅs ᴜɴᴛɪʟ ᴛʜᴇ ʙᴏᴛ sᴛᴀʀᴛs..."
    )
    os.system(f"kill -9 {os.getpid()} && python3 -m Anonymous")

@app.on_message(filters.command(["clone"]) & owner)
async def clone_bot(_, message):
    if len(message.command) < 2:
        return await message.reply_text("Please provide a bot token.\nUsage: /clone <bot_token>")
    
    token = message.command[1]
    
    try:
        # Create a new client with the provided token
        cloned_bot = Client(
            ":memory:",
            api_id=ap.API_ID,
            api_hash=ap.API_HASH,
            bot_token=token,
            in_memory=True
        )
        
        # Start the cloned bot
        await cloned_bot.start()
        bot_info = await cloned_bot.get_me()
        await cloned_bot.stop()
        
        await message.reply_text(
            f"Successfully cloned bot!\n"
            f"Username: @{bot_info.username}\n"
            f"ID: {bot_info.id}\n\n"
            f"You can now interact with this bot using its token."
        )
    except Exception as e:
        await message.reply_text(f"Failed to clone bot: {str(e)}")
