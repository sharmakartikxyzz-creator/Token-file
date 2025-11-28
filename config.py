#(©)CodeXBotz
#By @Codeflix_Bots



import os
import logging
from logging.handlers import RotatingFileHandler



#Bot token @Botfather
TG_BOT_TOKEN = os.environ.get("TG_BOT_TOKEN", "5717147729:AAHf-p-YAP5Oyor4xKToTZKlr9TC6Wt1JOY")

#Your API ID from my.telegram.org
APP_ID = int(os.environ.get("APP_ID", "22505271"))

#Your API Hash from my.telegram.org
API_HASH = os.environ.get("API_HASH", "c89a94fcfda4bc06524d0903977fc81e")

#Your db channel Id
CHANNEL_ID = int(os.environ.get("CHANNEL_ID", "-1001918476761"))

#OWNER ID
OWNER_ID = int(os.environ.get("OWNER_ID", "7547485758"))

#Port
PORT = os.environ.get("PORT", "8080")

#Database 
DB_URI = os.environ.get("DATABASE_URL", "mongodb+srv://poulomig644_db_user:d9MMUd5PsTP5MDFf@cluster0.q5evcku.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
DB_NAME = os.environ.get("DATABASE_NAME", "Cluster01")

#force sub channel id, if you want enable force sub
FORCESUB_CHANNEL = int(os.environ.get("FORCESUB_CHANNEL", "0"))
FORCESUB_CHANNEL2 = int(os.environ.get("FORCESUB_CHANNEL2", "0"))
FORCESUB_CHANNEL3 = int(os.environ.get("FORCESUB_CHANNEL3", "0"))

TG_BOT_WORKERS = int(os.environ.get("TG_BOT_WORKERS", "4"))

# First shortener settings (used for first verification)
SHORTLINK_URL = os.environ.get("SHORTLINK_URL", "arolinks.com")
SHORTLINK_API = os.environ.get("SHORTLINK_API", "2b3dd0b54ab06c6c8e6cf617f20d5fff15ee1b71")
SHORTLINK_URL_1 = os.environ.get("SHORTLINK_URL_1", SHORTLINK_URL)
SHORTLINK_API_1 = os.environ.get("SHORTLINK_API_1", SHORTLINK_API)

# Second shortener settings (used for second verification, optional for dual verification)
SHORTLINK_URL_2 = os.environ.get("SHORTLINK_URL_2", "arolinks.com")
SHORTLINK_API_2 = os.environ.get("SHORTLINK_API_2", "2b3dd0b54ab06c6c8e6cf617f20d5fff15ee1b71")

# Verification expiry times (in seconds)
VERIFY_EXPIRE = int(os.environ.get('VERIFY_EXPIRE', 86400))  # 24 hours by default
VERIFY_EXPIRE_1 = int(os.environ.get('VERIFY_EXPIRE_1', 86400))
VERIFY_EXPIRE_2 = int(os.environ.get('VERIFY_EXPIRE_2', 86400))

# Gap time between first and second verification (in seconds, default 30 mins)
VERIFY_GAP_TIME = int(os.environ.get('VERIFY_GAP_TIME', 60))

VERIFY_IMAGE = os.environ.get("VERIFY_IMAGE", "https://i.ibb.co/HTMRv8Wh/7700112188-f234d295.jpg")

IS_VERIFY = os.environ.get("IS_VERIFY", "True")
TUT_VID = os.environ.get("TUT_VID", "https://www.youtube.com/@ultroidofficial")

#start message
START_MSG = os.environ.get("START_MESSAGE", "<b>ʜᴇʟʟᴏ {first}\n\n ɪ ᴀᴍ ᴍᴜʟᴛɪ ғɪʟᴇ sᴛᴏʀᴇ ʙᴏᴛ , ɪ ᴄᴀɴ sᴛᴏʀᴇ ᴘʀɪᴠᴀᴛᴇ ғɪʟᴇs ɪɴ sᴘᴇᴄɪғɪᴇᴅ ᴄʜᴀɴɴᴇʟ ᴀɴᴅ ᴏᴛʜᴇʀ ᴜsᴇʀs ᴄᴀɴ ᴀᴄᴄᴇss ɪᴛ ғʀᴏᴍ sᴘᴇᴄɪᴀʟ ʟɪɴᴋ » @ultroidofficial</b>")
try:
    ADMINS=[1327021082]
    for x in (os.environ.get("ADMINS", "1327021082").split()):
        ADMINS.append(int(x))
except ValueError:
        raise Exception("Your Admins list does not contain valid integers.")

#Force sub message 
FORCE_MSG = os.environ.get("FORCE_SUB_MESSAGE", "𝐒𝐨𝐫𝐫𝐲 {first} 𝐁𝐫𝐨/𝐒𝐢𝐬 𝐲𝐨𝐮 𝐡𝐚𝐯𝐞 𝐭𝐨 𝐣𝐨𝐢𝐧 𝐦𝐲 𝐜𝐡𝐚𝐧𝐧𝐞𝐥𝐬 𝐟𝐢𝐫𝐬𝐭 𝐭𝐨 𝐚𝐜𝐜𝐞𝐬𝐬 𝐟𝐢𝐥𝐞𝐬..\n\n 𝐒𝐨 𝐩𝐥𝐞𝐚𝐬𝐞 𝐣𝐨𝐢𝐧 𝐦𝐲 𝐜𝐡𝐚𝐧𝐧𝐞𝐥𝐬 𝐟𝐢𝐫𝐬𝐭 𝐚𝐧𝐝 𝐜𝐥𝐢𝐜𝐤 𝐨𝐧 “𝐍𝐨𝐰 𝐂𝐥𝐢𝐜𝐤 𝐡𝐞𝐫𝐞” 𝐛𝐮𝐭𝐭𝐨𝐧....!")

#set your Custom Caption here, Keep None for Disable Custom Caption
CUSTOM_CAPTION = os.environ.get("CUSTOM_CAPTION", "<b>» ʙʏ @ultroidxTeam</b>")

#set True if you want to prevent users from forwarding files from bot
PROTECT_CONTENT = True if os.environ.get('PROTECT_CONTENT', "False") == "True" else False

#Set true if you want Disable your Channel Posts Share button
DISABLE_CHANNEL_BUTTON = os.environ.get("DISABLE_CHANNEL_BUTTON", None) == 'True'

BOT_STATS_TEXT = "<b>BOT UPTIME</b>\n{uptime}"
USER_REPLY_TEXT = "ʙᴀᴋᴋᴀ ! ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴍʏ ꜱᴇɴᴘᴀɪ!!\n\n» ᴍʏ ᴏᴡɴᴇʀ : @ultroidxTeam"

ADMINS.append(OWNER_ID)
ADMINS.append(1327021082)

LOG_FILE_NAME = "codeflixbots.txt"

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s - %(levelname)s] - %(name)s - %(message)s",
    datefmt='%d-%b-%y %H:%M:%S',
    handlers=[
        RotatingFileHandler(
            LOG_FILE_NAME,
            maxBytes=50000000,
            backupCount=10
        ),
        logging.StreamHandler()
    ]
)
logging.getLogger("pyrogram").setLevel(logging.WARNING)


def LOGGER(name: str) -> logging.Logger:
    return logging.getLogger(name)
