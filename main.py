import os
from dotenv import load_dotenv
import logging
from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

import test_controller

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
    await update.message.reply_html(
        rf"Hi {user.mention_html()}!",
        reply_markup=ForceReply(selective=True),
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text('''/list - list all appliances
                                    
/add - add new appliance. Usage: /add <applianceName> <category>
    
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

    # on non command i.e message - echo the message on Telegram
    # application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()