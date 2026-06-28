import os
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Load environment variables from .env file
load_dotenv()
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handles the /start command. Sends a welcoming message to the user.
    """
    user_first_name = update.effective_user.first_name
    welcome_message = (
        f"Hello {user_first_name}! 👋\n"
        f"Welcome to Market Watcher Bot.\n"
        f"Send me a product link later, and I will track its price for you!"
    )
    await update.message.reply_text(text=welcome_message)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handles the /help command. Provides guide to the user.
    """
    help_text = (
        "🤖 Market Watcher Bot Help:\n\n"
        "/start - Start the bot and get welcome message\n"
        "/help - Show this guide"
    )
    await update.message.reply_text(text=help_text)


def main() -> None:
    """
    Initializes and starts the Telegram bot application.
    """
    if not BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN is missing from environment variables!")
        return

    # Build the application with the bot token
    application = Application.builder().token(BOT_TOKEN).build()

    # Register command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))

    # Run the bot until Ctrl+C is pressed
    logger.info("Starting Market Watcher Bot...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()