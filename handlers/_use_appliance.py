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

APPLIANCE_NAME_USE = range(1)

async def start_use_appliance(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_appliance = db_controller.get_all_appliance(update.effective_message.chat_id)

    if len(user_appliance) == 0:
        await update.message.reply_text(
            "No appliance found. Please add an appliance first."
        )
        return ConversationHandler.END

    appliance_name = ''
    for x in user_appliance:
        appliance_name += f"{user_appliance.index(x) + 1}. Name: {x['name']}\n    Category: {x['category']}\n    Status: {"ON" if x['status'] else 'OFF'}" + '\n'

    await update.message.reply_text(
        "Which appliance do you want to turn on?"
        "Usage: <appliance no.>\n\n"
        f"{appliance_name}"
    )

    return APPLIANCE_NAME_USE

async def use_appliance(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None: 
    user = update.message.from_user
    logger.info("User %s: %s", user.first_name, update.message.text)

    if (update.message.text.isdigit()):
        if int(update.message.text) - 1 < len(db_controller.get_all_appliance(update.effective_message.chat_id)):
            db_controller.update_appliance_status(update.effective_message.chat_id, update.message.text)

            user_appliance = db_controller.get_all_appliance(update.effective_message.chat_id)
            appliance_name = ''
            for x in user_appliance:
                appliance_name += f"{user_appliance.index(x) + 1}. Name: {x['name']}\n    Category: {x['category']}\n    Status: {"ON" if x['status'] else 'OFF'}" + '\n'

            await update.message.reply_text(
                "Appliance status updated!\n\n"
                f"{appliance_name}"
            )
        else: 
            await update.message.reply_text(
                "Appliance not found."
            )

    return ConversationHandler.END
    