import os
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, PicklePersistence

# Import handlers from the modular handlers package
from handlers.commands import start_command, help_command
from handlers.messages import handle_message
from handlers.callbacks import handle_callback
from handlers.jobs import check_prices_job

# Load environment variables from .env file
load_dotenv()
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def main() -> None:
    """
    Initializes and starts the Telegram bot application with persistence and job queue.
    """
    if not BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN is missing from environment variables!")
        return

    # Setup persistence
    persistence = PicklePersistence(filepath="market_watcher_data.pickle")

    # Build the application
    application = Application.builder().token(BOT_TOKEN).persistence(persistence).build()

    # Register command and message handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Register the inline button callback handler
    application.add_handler(CallbackQueryHandler(handle_callback))

    # Setup JobQueue to check prices periodically
    job_queue = application.job_queue
    job_queue.run_repeating(check_prices_job, interval=60, first=10) #type: ignore


    # Run the bot
    logger.info("Starting Market Watcher Bot with JobQueue and Persistence...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()