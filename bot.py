import os
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler

# Import handlers from the modular handlers package
from handlers.commands import start_command, help_command

# Load environment variables from .env file
load_dotenv()
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Enable logging to monitor bot status and errors
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def main() -> None:
    """
    Initializes and starts the Telegram bot application.
    """
    if not BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN is missing from environment variables!")
        return

    # Build the application with the bot token
    application = Application.builder().token(BOT_TOKEN).build()

    # Register command handlers imported from commands module
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))

    # Run the bot until Ctrl+C is pressed
    logger.info("Starting Market Watcher Bot...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()