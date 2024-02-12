import os
from dotenv import load_dotenv
import logging
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import Application, CommandHandler, ContextTypes, ConversationHandler, MessageHandler, filters

import controllers.test_controller as test_controller
import controllers.db_controller as db_controller

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

/turnon - turn on appliance. Usage: /turnon <applianceId>
    
/turnoff - turn off appliance. Usage: /turnoff <applianceId>
    
-- sensor control --
    
/automoisture - start auto moisture updates.
    
/stopautomoisture - stop auto moisture updates.
    
-- security control --
    
/setpasswd - set new password.
    
/setkeycard - set new keycard.
    
/intruderalert - send intruder alert if detected.
    
/stopintruderalert - stop intruder alert.''')


# async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     """Echo the user message."""
#     await update.message.reply_text(update.message.text)

# async def send_auto_moisture(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     await update.message.reply_text(test_controller.say_hello())
    
def remove_job_if_exists(name: str, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Remove job with given name. Returns whether job was removed."""
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True


# automoisture
async def automoisture_callback(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send the alarm message."""
    job = context.job
    await context.bot.send_message(job.chat_id, text=f"{job.data}")

async def set_automoisture(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Add a job to the queue."""
    chat_id = update.effective_message.chat_id
    try:
        job_removed = remove_job_if_exists(str(chat_id), context)
        context.job_queue.run_repeating(automoisture_callback, interval=3, chat_id=chat_id, name=str(chat_id), data=f"{test_controller.say_hello()}")

        text = "Auto moisture monitoring successfully started!"
        if job_removed:
            text += " Previous one was removed."
        await update.effective_message.reply_text(text)

    except (IndexError, ValueError):
        await update.effective_message.reply_text("Usage: /setautomoisture")

async def unset_automoisture(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Remove the job if the user changed their mind."""
    chat_id = update.message.chat_id
    job_removed = remove_job_if_exists(str(chat_id), context)
    text = "Auto moisture monitoring successfully cancelled!" if job_removed else "You have no active automoisture."
    await update.message.reply_text(text)


# intruder alert
async def intruder_alert_callback(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send the alarm message."""
    job = context.job
    if job.data == "Object in way":
        await context.bot.send_message(job.chat_id, text=f"{job.data}")
    # await context.bot.send_message(job.chat_id, text=f"{job.data}")

async def set_intruder_alert(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Add a job to the queue."""
    chat_id = update.effective_message.chat_id
    try:
        job_removed = remove_job_if_exists(str(chat_id), context)
        context.job_queue.run_repeating(intruder_alert_callback, interval=1, chat_id=chat_id, name=str(chat_id), data=f"{test_controller.paisley()}")

        text = "Intruder alert enabled!"
        if job_removed:
            text += " Previous one was removed."
        await update.effective_message.reply_text(text)

    except (IndexError, ValueError):
        await update.effective_message.reply_text("Error: cannot set intruder alert")

async def unset_intruder_alert(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Remove the job if the user changed their mind."""
    chat_id = update.message.chat_id
    job_removed = remove_job_if_exists(str(chat_id), context)
    text = "Intruder alert disabled!" if job_removed else "You have no active intruder alert."
    await update.message.reply_text(text)


# add appliance
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


# remove appliance
APPLIANCE_NAME_REMOVE = range(1)

async def start_remove_appliance(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_appliance = db_controller.get_all_appliance(update.effective_message.chat_id)
    appliance_name = ''
    for x in user_appliance:
        appliance_name += f'{user_appliance.index(x) + 1}. ' + x['name'] + '\n'

    await update.message.reply_text(
        "Which appliance do you want to remove?"
        "Send /cancel to stop talking to me.\n"
        "Usage: <appliance no.>\n\n"
        f"{appliance_name}"
    )

    return APPLIANCE_NAME_REMOVE

async def remove_appliance(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None: 
    user = update.message.from_user
    logger.info("User %s: %s", user.first_name, update.message.text)

    if (update.message.text.isdigit()):
        if int(update.message.text) - 1 < len(db_controller.get_all_appliance(update.effective_message.chat_id)):
            db_controller.remove_appliance(update.effective_message.chat_id, update.message.text)

            await update.message.reply_text(
                "Appliance removed!"
            )
        else: 
            await update.message.reply_text(
                "Appliance not found."
            )
        # db_controller.remove_appliance(update.effective_message.chat_id, update.message.text)

    return ConversationHandler.END
    
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

    # on non command i.e message - echo the message on Telegram
    # application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()