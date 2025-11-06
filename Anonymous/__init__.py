# (©) Anonymous Emperor

import logging
import importlib
import os
from pyrogram import Client
from Anonymous.config import Config
from Anonymous.config import Config as c
from datetime import datetime
from sys import exit as sysexit
from time import time
from sys import stdout, version_info
from os import environ, listdir, mkdir, path
from Anonymous.filters import *
from . import filters
import pytz
from telegram.ext import Application
from logging import (INFO, WARNING, FileHandler, StreamHandler, basicConfig,
                     getLogger)

LOG_DATETIME = datetime.now().strftime("%d_%m_%Y-%H_%M_%S")
LOGDIR = f"{__name__}/logs"

# Make Logs directory if it does not exixts
if not path.isdir(LOGDIR):
    mkdir(LOGDIR)

LOGFILE = f"{LOGDIR}/{__name__}_{LOG_DATETIME}_log.txt"

file_handler = FileHandler(filename=LOGFILE)
stdout_handler = StreamHandler(stdout)

basicConfig(
    format="%(asctime)s - [Anonymous] - %(levelname)s - %(message)s",
    level=INFO,
    handlers=[file_handler, stdout_handler],
)

getLogger("pyrogram").setLevel(WARNING)
getLogger("telegram").setLevel(WARNING)
getLogger("httpx").setLevel(WARNING)
getLogger("telegram-ext").setLevel(WARNING)

LOGGER = getLogger(__name__)

# if version < 3.9, stop bot.
if version_info[0] < 3 or version_info[1] < 7:
    LOGGER.error(
        (
            "You MUST have a Python Version of at least 3.7!\n"
            "Multiple features depend on this. Bot quitting."
        ),
    )
    sysexit(1)  # Quit the Script

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Anonymous")

# Create a new instance of the Pyrogram Client (bot)
app = Client(
    "app",
    bot_token=Config.BOT_TOKEN,
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
    workers=10
)

application = Application.builder().token(Config.TOKEN).build()

tgbot = application 

API_ID = c.API_ID
API_HASH = c.API_HASH
BOT_TOKEN = c.BOT_TOKEN
TOKEN = c.BOT_TOKEN
OWNER_ID = c.OWNER_ID
MONGO_URI = c.MONGO_URI
DB_URI = c.MONGO_URI
LOGS = c.LOGS
LOG_CHANNEL_ID = c.LOGS
SESSION = c.SESSION

ubot = Client(
    "userbot",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION,
    workers=8,
    max_concurrent_transmissions=30
)


# Dynamically load all plugins in the "Anonymous/plugins" directory
PLUGIN_PATH = os.path.join(os.path.dirname(__file__), "plugins")
for file in os.listdir(PLUGIN_PATH):
    if file.endswith(".py") and not file.startswith("__"):
        module_name = f"Anonymous.plugins.{file[:-3]}"
        try:
            importlib.import_module(module_name)
            logger.info(f"✅ Successfully loaded module: {module_name}")
        except Exception as e:
            logger.error(f"❌ Failed to load module: {module_name} - {e}")
