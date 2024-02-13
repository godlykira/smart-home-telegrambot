import os
from dotenv import load_dotenv
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, ConversationHandler, MessageHandler, filters

import controllers.db_controller as db_controller

from handlers._moisture import set_automoisture, unset_automoisture
from handlers._intruder_alert import set_intruder_alert, unset_intruder_alert
from handlers._add_appliance import get_categories, start_add_appliance, appliance_category, appliance_name, cancel_add_appliance, APPLIANCE_CATEGORY, APPLIANCE_NAME
from handlers._rm_appliance import start_remove_appliance, remove_appliance, APPLIANCE_NAME_REMOVE
from handlers._use_appliance import start_use_appliance, use_appliance, APPLIANCE_NAME_USE
from handlers._add_passkey import start_add_password, add_password, PASSKEY

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments update and
# context.
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    logger.info("User %s started the conversation.", user.first_name)

    # Add user to database
    db_controller.create_user_db(update.effective_message.chat_id)

    await update.message.reply_html(
        rf"Hi {user.mention_html()}!",
        # reply_markup=ForceReply(selective=True),
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text('''/list - list all appliances
                                    
/addappliance - add new appliance.
/removeappliance - remove appliance.
    
-- turn on/off appliances --

/toggle - turn on/off appliance. Usage: /toggle <appliance_no>
    
-- sensor control --
    
/automoisture - start auto moisture updates.
/stopautomoisture - stop auto moisture updates.
    
-- security control --

/enablesecurity - enable security.
/disablesecurity - disable security.
    
/setpasswd - set new password.
/setkeycard - set new keycard.
                                    
/intruderalert - send intruder alert if detected.
/stopintruderalert - stop intruder alert.''')


# async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     """Echo the user message."""
#     await update.message.reply_text(update.message.text)

# async def send_auto_moisture(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     await update.message.reply_text(test_controller.say_hello())

def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TOKEN).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    application.add_handler(CommandHandler("automoisture", set_automoisture))
    application.add_handler(CommandHandler("stopautomoisture", unset_automoisture))

    application.add_handler(CommandHandler("intruderalert", set_intruder_alert))
    application.add_handler(CommandHandler('stopintruderalert', unset_intruder_alert))

    conv_addAppliance = ConversationHandler(
        entry_points=[CommandHandler('addappliance', start_add_appliance)],
        states={
            APPLIANCE_CATEGORY: [MessageHandler(filters.Regex(f"^({get_categories()['regex']})$"), appliance_category)],
            APPLIANCE_NAME: [MessageHandler(filters.TEXT, appliance_name)],
        },
        fallbacks=[CommandHandler("cancel", cancel_add_appliance)],
    )
    application.add_handler(conv_addAppliance)

    conv_removeAppliance = ConversationHandler(
        entry_points=[CommandHandler('removeappliance', start_remove_appliance)],
        states={
            APPLIANCE_NAME_REMOVE: [MessageHandler(filters.TEXT, remove_appliance)],
        },
        fallbacks=[],
    )
    application.add_handler(conv_removeAppliance)

    conv_useAppliance = ConversationHandler(
        entry_points=[CommandHandler('toggle', start_use_appliance)],
        states={
            APPLIANCE_NAME_USE: [MessageHandler(filters.TEXT, use_appliance)],
        },
        fallbacks=[],
    )
    application.add_handler(conv_useAppliance)

    conv_addpasskey = ConversationHandler(
        entry_points=[CommandHandler('setpasswd', start_add_password)],
        states={
            PASSKEY: [MessageHandler(filters.TEXT, add_password)],
        },
        fallbacks=[],
    )
    application.add_handler(conv_addpasskey)

    # on non command i.e message - echo the message on Telegram
    # application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()