import logging
from telegram import Update
from telegram.ext import ContextTypes

import controllers.test_controller as test_controller

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

async def intruder_alert_callback(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send the alarm message."""
    job = context.job
    if job.data == "Object in way":
        await context.bot.send_message(job.chat_id, text=f"{job.data}")
    # await context.bot.send_message(job.chat_id, text=f"{job.data}")
        
def remove_job_if_exists(name: str, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Remove job with given name. Returns whether job was removed."""
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True

async def set_intruder_alert(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Add a job to the queue."""
    chat_id = update.effective_message.chat_id
    try:
        job_removed = remove_job_if_exists(str(chat_id), context)
        context.job_queue.run_repeating(intruder_alert_callback, interval=1, chat_id=chat_id, name=str(chat_id), data=f"{test_controller.infrared()}")

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
