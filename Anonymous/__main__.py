import importlib
import logging
import random
import sys
import time
from asyncio import get_event_loop

from Anonymous import app, ubot, application
from Anonymous.plugins import ALL_MODULES
from Anonymous.config import StartPic

from pyrogram.enums import ParseMode
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

LOGGER = logging.getLogger(__name__)
LOGS = "@Raiden_Support"  # Your logging channel
MAX_RESTART_ATTEMPTS = 5  # Maximum number of restart attempts before giving up
RESTART_DELAY = 10  # Delay between restart attempts in seconds

async def send_startup_message():
    try:
        image_url = random.choice(StartPic)
        caption = (
            "**🔥 𝙱𝚘𝚝 𝙷𝚊𝚜 𝚂𝚝𝚊𝚛𝚝𝚎𝚍!**\n\n"
            "✨ **I'm here to make your group safer and more fun!**\n\n"
            "__Tap the button below to explore my features.__\n\n"
            "🔒 **Protection Suite:**\n"
            " - Auto-delete edited messages\n"
            " - `/setdelay` for timed deletions\n"
            " - Word & link filters\n"
            " - `/permit` system\n\n"
            "🎮 **Toji Word Game:**\n"
            " - `/new` word challenge\n"
            " - Leaderboard & hints\n\n"
            "🛠️ **Moderation:**\n"
            " - Purge, ban, mute\n"
            " - Clean messages\n\n"
            "👑 **Admin Tools:**\n"
            " - Word control, broadcast\n"
            " - Group stats, much more...\n\n"
            "🚀 *Let's build an awesome group!*"
        )
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("✨ Explore Features", url="https://t.me/Toji_ProXBot?start=help")]
        ])

        await app.send_photo(
            chat_id=LOGS,
            photo=image_url,
            caption=caption,
            reply_markup=buttons,
            parse_mode=ParseMode.MARKDOWN
        )
        LOGGER.info("✅ Sent startup notification")
    except Exception as e:
        LOGGER.error(f"❌ Startup message error: {e}")

async def send_shutdown_message():
    try:
        await app.send_message(
            chat_id=LOGS,
            text="🛑 **Bot shutdown completed**\n\nAll services stopped safely.",
            parse_mode=ParseMode.MARKDOWN
        )
        LOGGER.info("✅ Sent shutdown notification")
    except Exception as e:
        LOGGER.error(f"❌ Shutdown message error: {e}")

async def send_restart_notification(attempt):
    try:
        await app.send_message(
            chat_id=LOGS,
            text=f"♻️ **Bot restarting...** (Attempt {attempt}/{MAX_RESTART_ATTEMPTS})\n\n"
                 f"Reason: Previous instance crashed or was terminated.",
            parse_mode=ParseMode.MARKDOWN
        )
    except Exception as e:
        LOGGER.error(f"❌ Restart notification error: {e}")

async def start_services():
    """Initialize and start all bot services"""
    try:
        # Start Pyrogram clients
        await app.start()
        await ubot.start()
        LOGGER.info("🔥 Pyrogram clients started")
        
        # Start PTB application
        await application.initialize()
        await application.start()
        await application.updater.start_polling(drop_pending_updates=True)
        LOGGER.info("🤖 PTB polling started")
        
        # Send startup notification
        await send_startup_message()
        
    except Exception as e:
        LOGGER.critical(f"🚨 Service startup failed: {e}")
        raise

async def stop_services():
    """Gracefully stop all bot services"""
    try:
        # Stop PTB first
        if application.running:
            await application.updater.stop()
            await application.stop()
            await application.shutdown()
            LOGGER.info("🛑 PTB services stopped")
        
        # Stop Pyrogram clients
        await app.stop()
        await ubot.stop()
        LOGGER.info("🛑 Pyrogram clients stopped")
        
    except Exception as e:
        LOGGER.error(f"⚠️ Service stop error: {e}")

def main():
    # Load all plugin modules
    for module in ALL_MODULES:
        try:
            importlib.import_module(f"Anonymous.plugins.{module}")
            LOGGER.debug(f"✅ Loaded module: {module}")
        except Exception as e:
            LOGGER.error(f"❌ Module load failed: {module} - {e}")
    
    LOGGER.info("📦 All modules loaded")
    
    restart_attempts = 0
    
    while restart_attempts < MAX_RESTART_ATTEMPTS:
        loop = get_event_loop()
        
        try:
            # Start all services
            loop.run_until_complete(start_services())
            LOGGER.info(f"🚀 Bot is now operational (Attempt {restart_attempts + 1}/{MAX_RESTART_ATTEMPTS})")
            
            # Keep running
            loop.run_forever()
            
        except (KeyboardInterrupt, SystemExit):
            LOGGER.warning("🛑 Received shutdown signal")
            break
            
        except Exception as e:
            LOGGER.critical(f"💥 Fatal error: {e}")
            restart_attempts += 1
            
            # Send restart notification
            try:
                loop.run_until_complete(send_restart_notification(restart_attempts))
            except:
                pass
            
            if restart_attempts < MAX_RESTART_ATTEMPTS:
                LOGGER.info(f"♻️ Attempting to restart in {RESTART_DELAY} seconds...")
                time.sleep(RESTART_DELAY)
            else:
                LOGGER.error(f"⛔ Max restart attempts ({MAX_RESTART_ATTEMPTS}) reached. Giving up.")
                break
            
        finally:
            # Clean shutdown sequence
            LOGGER.info("🧹 Starting shutdown...")
            try:
                loop.run_until_complete(send_shutdown_message())
                loop.run_until_complete(stop_services())
            except:
                pass
            loop.close()
            LOGGER.info("👋 Shutdown complete")

    if restart_attempts >= MAX_RESTART_ATTEMPTS:
        LOGGER.critical("🆘 Bot failed to recover after multiple attempts. Exiting.")
        sys.exit(1)

if __name__ == "__main__":
    main()
