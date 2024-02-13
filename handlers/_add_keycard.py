import logging
from telegram import Update
from telegram.ext import ContextTypes

import controllers.test_controller as test_controller
import controllers.db_controller as db_controller

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)
        
def remove_job_if_exists(name: str, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Remove job with given name. Returns whether job was removed."""
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True

async def callback(context: ContextTypes.DEFAULT_TYPE) -> None:
    job = context.job
    if job.data != "":
        job_removed = remove_job_if_exists(str(job.chat_id), context)
        text = "Card registered" if job_removed else "You have no active card registration."

        # add to db
        db_controller.add_keycard(job.chat_id, job.data)

        await context.bot.send_message(job.chat_id, text=f"{text}")
    # await context.bot.send_message(job.chat_id, text=f"{job.data}")

async def start_get_keycard(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Place keycard on the card reader"
    )

    await get_keycard(update, context)

async def get_keycard(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Add a job to the queue."""
    chat_id = update.effective_message.chat_id
    try:
        context.job_queue.run_repeating(callback, interval=1, chat_id=chat_id, name=str(chat_id), data=f"{test_controller.register_card()}")

    except (IndexError, ValueError):
        await update.effective_message.reply_text("Error: cannot set intruder alert")
