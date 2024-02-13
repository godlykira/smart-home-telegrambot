import logging
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

import controllers.db_controller as db_controller

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

PASSKEY = range(1)

async def start_add_password(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Enter passkey:")

    return PASSKEY

async def add_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    logger.info("Passkey of %s: %s", user.first_name, update.message.text)

    # save to db
    db_controller.add_passkey(update.effective_message.chat_id, update.message.text)

    await update.message.reply_text(
        "Thanks! I will remember this."
    )

    return ConversationHandler.END