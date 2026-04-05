import os
from dotenv import load_dotenv

load_dotenv()

API_ID         = int(os.environ.get("API_ID", 0))
API_HASH       = os.environ.get("API_HASH", "")
STRING_SESSION = os.environ.get("STRING_SESSION", "")
BOT_TOKEN      = os.environ.get("BOT_TOKEN", "")
OWNER_ID       = int(os.environ.get("OWNER_ID", 0))
OWNER_USERNAME = os.environ.get("OWNER_USERNAME", "")
BOT_USERNAME   = os.environ.get("BOT_USERNAME", "")
START_IMAGE    = os.environ.get("START_IMAGE", "")
LOG_GROUP_ID   = int(os.environ.get("LOG_GROUP_ID", 0))

_sudo_env = os.environ.get("SUDO_USERS", "")
SUDO_USERS = list(set(
    [OWNER_ID] +
    [int(uid.strip()) for uid in _sudo_env.split()
     if uid.strip().isdigit()]
))

def get_sudo_list():
    try:
        from database.sudo_db import get_all_sudos
        db_sudos = [s["user_id"] for s in get_all_sudos()]
    except Exception:
        db_sudos = []
    return list(set([OWNER_ID] + db_sudos))
