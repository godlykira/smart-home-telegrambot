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

APPLIANCE_NAME_REMOVE = range(1)


async def start_remove_appliance(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    Removes an appliance specified by the user, if any, from the user's list of appliances.

    Args:
        update (Update): The incoming update for this handler.
        context (ContextTypes.DEFAULT_TYPE): The context for this handler.

    Returns:
        None
    """
    user_appliance = db_controller.get_all_appliance(update.effective_message.chat_id)

    if len(user_appliance) == 0:
        await update.message.reply_text(
            "No appliance found. Please add an appliance first."
        )
        return ConversationHandler.END

    appliance_name = ""
    for x in user_appliance:
        appliance_name += f"{user_appliance.index(x) + 1}. " + x["name"] + "\n"

    await update.message.reply_text(
        "Which appliance do you want to remove?"
        "Usage: <appliance no.>\n\n"
        f"{appliance_name}"
    )

    return APPLIANCE_NAME_REMOVE


async def remove_appliance(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Asynchronously removes an appliance from the chat's database based on the user input.

    Args:
    - update (Update): The incoming update from the user.
    - context (ContextTypes.DEFAULT_TYPE): The context in which the update is being handled.

    Returns:
    - None
    """
    user = update.message.from_user
    logger.info("User %s: %s", user.first_name, update.message.text)

    if update.message.text.isdigit():
        if int(update.message.text) - 1 < len(
            db_controller.get_all_appliance(update.effective_message.chat_id)
        ):
            db_controller.remove_appliance(
                update.effective_message.chat_id, update.message.text
            )

            user_appliance = db_controller.get_all_appliance(
                update.effective_message.chat_id
            )
            appliance_name = ""
            for x in user_appliance:
                appliance_name += f"{user_appliance.index(x) + 1}. " + x["name"] + "\n"

            await update.message.reply_text(
                "Appliance removed!\n\n" f"{appliance_name}"
            )
        else:
            await update.message.reply_text("Appliance not found.")
        # db_controller.remove_appliance(update.effective_message.chat_id, update.message.text)

    return ConversationHandler.END
