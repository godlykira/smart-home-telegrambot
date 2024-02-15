import logging
from telegram import Update
from telegram.ext import ContextTypes

# ##########################################################################

import controllers.controller as controller

# ##########################################################################

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


async def intruder_alert_callback(context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Send the alarm message if an intruder is detected.

    Args:
    - context: The context object containing information about the job and bot.

    Returns:
    - None
    """
    job = context.job  # Extract the chat ID from the context
    condition = (
        await controller.ultrasonic()
    )  # Check the ultrasonic sensor for presence
    if condition:  # If presence is detected
        await context.bot.send_message(
            job.chat_id, text="Presence Detected"
        )  # Send a message indicating presence
    # await context.bot.send_message(job.chat_id, text=f"{job.data}")  # Commented out line, not removed


def remove_job_if_exists(name: str, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Remove job with the given name if it exists.

    Args:
    name (str): The name of the job to be removed.
    context (ContextTypes.DEFAULT_TYPE): The context containing the job queue.

    Returns:
    bool: True if job was removed, False otherwise.
    """
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True


async def set_intruder_alert(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Add a job to the queue to enable intruder alert."""
    # Get the chat ID from the update
    chat_id = update.effective_message.chat_id

    # Remove any existing job for the current chat ID
    try:
        job_removed = remove_job_if_exists(str(chat_id), context)
        # Schedule a repeating job for the intruder alert callback
        context.job_queue.run_repeating(
            intruder_alert_callback, interval=1, chat_id=chat_id, name=str(chat_id)
        )

        text = "Intruder alert enabled!"
        if job_removed:
            text += " Previous one was removed."
        # Send a message to confirm that the intruder alert is enabled
        await update.effective_message.reply_text(text)

    except (IndexError, ValueError):
        # Handle the exception if setting the intruder alert fails
        await update.effective_message.reply_text("Error: cannot set intruder alert")


async def unset_intruder_alert(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Remove the intruder alert job if the user changed their mind.

    Args:
        update (telegram.Update): The incoming update from Telegram.
        context (telegram.ext.CallbackContext): The context for the handler.
    """
    chat_id = update.message.chat_id  # Get the chat ID from the update
    job_removed = remove_job_if_exists(
        str(chat_id), context
    )  # Remove the job if it exists
    text = (
        "Intruder alert disabled!"
        if job_removed
        else "You have no active intruder alert."
    )
    await update.message.reply_text(text)  # Send the appropriate message as a reply
