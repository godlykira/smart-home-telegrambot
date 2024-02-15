import logging
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

import threading
from queue import Queue

import controllers.db_controller as db_controller
import controllers.controller as controller

# Multithreading to read the ADC values
queue = Queue()
thread = threading.Thread(target=controller.current, args=(queue,))
thread.start()

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

APPLIANCE_NAME_USE = range(1)


async def start_use_appliance(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    Asynchronous function to start using an appliance.

    Args:
        update (Update): The incoming update for the handler.
        context (ContextTypes.DEFAULT_TYPE): The context for the handler.

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
        appliance_name += f"{user_appliance.index(x) + 1}. Name: {x['name']}\n    Category: {x['category']}\n    Status: {'ON' if x['status'] else 'OFF'} \n\n"

    await update.message.reply_text(
        "Which appliance do you want to turn on?"
        "Usage: <appliance no.>\n\n"
        f"{appliance_name}"
    )

    return APPLIANCE_NAME_USE


async def use_appliance(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    An asynchronous function to use an appliance, taking an update and context as parameters and returning None.
    """
    user = update.message.from_user
    logger.info("User %s: %s", user.first_name, update.message.text)

    if update.message.text.isdigit():
        if int(update.message.text) - 1 < len(
            db_controller.get_all_appliance(update.effective_message.chat_id)
        ):
            max_current = queue.get() if not queue.empty() else 1023
            category = db_controller.get_all_appliance(
                update.effective_message.chat_id
            )[int(update.message.text) - 1]["category"]
            current = db_controller.get_current(category)
            total_current = db_controller.user_total_usage(
                update.effective_message.chat_id
            )

            # print(max_current, category ,current, total_current)

            if total_current + current > max_current:
                await update.message.reply_text(
                    "Cannot use this appliance. The maximum current is reached."
                )
            else:
                print("iN ELSE STATEMENT")
                db_controller.update_appliance_status(
                    update.effective_message.chat_id, update.message.text
                )

                user_appliance = db_controller.get_all_appliance(
                    update.effective_message.chat_id
                )
                appliance_name = ""
                for x in user_appliance:
                    appliance_name += f"{user_appliance.index(x) + 1}. Name: {x['name']}\n    Category: {x['category']}\n    Status: {'ON' if x['status'] else 'OFF'} \n\n"

                for x in user_appliance:
                    if x["category"] == "lights":
                        print("status", x["status"])
                        controller.light(x["status"])

                await update.message.reply_text(
                    "Appliance status updated!\n\n" f"{appliance_name}"
                )
        else:
            await update.message.reply_text("Appliance not found.")

    return ConversationHandler.END
