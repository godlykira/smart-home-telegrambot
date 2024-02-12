import logging
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import ContextTypes, ConversationHandler

import controllers.db_controller as db_controller

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

APPLIANCE_CATEGORY, APPLIANCE_NAME = range(2)

def get_categories() -> int:
    """
    Function to retrieve categories from the database and generate a regex pattern.
    Returns a dictionary containing the categories and the generated regex pattern.
    """
    categories = db_controller.get_categories()['categories']
    regex = ''
    for x in categories[0]:
        regex += x + '|'
    regex = regex[:-1]

    return {
        'categories': categories,
        'regex': regex
    }

async def start_add_appliance(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    reply_keyboard = get_categories()['categories']

    await update.message.reply_text(
        "Hi! I'm Smart Home. I can help you add appliances. "
        "Send /cancel to stop talking to me.\n\n"
        "Select your appliance category:",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="appliance category"
        ),
    )

    return APPLIANCE_CATEGORY

async def appliance_category(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the selected gender and asks for a photo."""
    user = update.message.from_user
    logger.info("Appliance category of %s: %s", user.first_name, update.message.text)

    # add to temp
    db_controller.add_to_temp(update.effective_message.chat_id, update.message.text)

    await update.message.reply_text(
        "so I know what your appliance is. Now give a name to your appliance: ",
        reply_markup=ReplyKeyboardRemove(),
    )

    return APPLIANCE_NAME

async def appliance_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the photo and asks for a location."""
    user = update.message.from_user
    logger.info("Appliance name of %s: %s", user.first_name, update.message.text)

    # add to temp
    db_controller.add_to_temp(update.effective_message.chat_id, update.message.text)

    # save to db
    db_controller.add_appliance(update.effective_message.chat_id)

    await update.message.reply_text(
        "Thanks! I will remember this."
    )

    return ConversationHandler.END

async def cancel_add_appliance(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("User %s canceled the add appliance", user.first_name)
    await update.message.reply_text(
        "Bye! I hope we can talk again some day.", reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END