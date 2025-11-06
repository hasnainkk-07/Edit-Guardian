# (©) Anonymous Emperor

from pyrogram import filters

LOGS = -1002105665930

StartPic = [
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

class Config:
    API_ID = 12345678  # Replace with your API ID
    API_HASH = "e12488391771ajajkamb"  # Replace with your API Hash
    BOT_TOKEN = "BOT_TOKEN"  # Replace with your Bot Token generate from @BotFather
    TOKEN = BOT_TOKEN
    MONGO_URI = "MONGO_DB_URL"  # Replace with your MongoDB URI
    OWNERS = [
        6346273488,  # (Creator)
        1805959544,  #  (Sukuna)
        1284920298,  # (Romeo Sama)
        5907205317,  # (Karma)
        5881613383,  # ( Anox )
    ]  # Replace with the owner IDs
    DATABASE_NAME = "AnonymousDB"
    LOGS = -1002105665930 # Replace with your logs channel Id
    SESSION = "STRING_SESSION"    # String Session for userbot
    LOG_CHANNEL_ID = -1002105665930 # Replace with your logs channel Id 
    BOT_USERNAME = "Toji_ProXBot"
    PREFIX_HANDLER = ["/", "!", "toji ", "Toji "]
    BOT_NAME = "Toji • Fushiguro"
    OWNER_ID = 6346273488
    DEV_USERS = [5907205317, 5881613383, 1284920298, 1805959544, 8171988347]


OWNER = 6346273488
DEVUSERS = [5907205317, 5881613383, 1284920298, 1805959544, 8171988347]
    
DEV_LEVEL = set(DEVUSERS + [int(OWNER)])



SUDOERS = filters.user()
BANNED_USERS = filters.user()

