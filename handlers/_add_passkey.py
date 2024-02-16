import logging
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

# ##########################################################################

import controllers.db_controller as db_controller

# ##########################################################################

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

PASSKEY = range(1)


async def start_add_password(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Asynchronous function to start the process of adding a password.
    Takes in an update object and a context object as parameters.
    Returns an integer representing the passkey.
    """
    await update.message.reply_text("Enter passkey:")

    return PASSKEY


async def add_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Asynchronously adds a password from the update message to the database, and replies with a success or failure message.

    Args:
        update (Update): The incoming update.
        context (ContextTypes.DEFAULT_TYPE): The context of the incoming update.

    Returns:
        ConversationHandler.END: The end state of the conversation handler.
    """
    user = update.message.from_user
    logger.info("Passkey of %s: %s", user.first_name, update.message.text)

    if update.message.text.isdigit() and len(update.message.text) == 8:
        # save to db
        db_controller.add_passkey(update.effective_message.chat_id, update.message.text)

        await update.message.reply_text("Thanks! I will remember this.")
    else:
        await update.message.reply_text(
            "Keypass should be only number and must be 8 digits."
        )

    return ConversationHandler.END
