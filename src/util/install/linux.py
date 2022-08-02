import logging
import os.path

logger = logging.getLogger("discord_fm").getChild(__name__)


def get_app_folder():
    return os.path.expanduser(f"~/.discord_fm")
