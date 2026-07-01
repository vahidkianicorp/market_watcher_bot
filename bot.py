import os
import logging
from dotenv import load_dotenv
from telegram import Update, BotCommand
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


async def post_init(application: Application) -> None:
    """
    Executed after the bot application is initialized.
    Sets up the persistent bot menu commands.
    """
    bot_commands = [
        BotCommand("start", "Start the bot and open main menu"),
        BotCommand("help", "Show help guide and usage instructions")
    ]
    await application.bot.set_my_commands(bot_commands)
    logger.info("Persistent bot menu commands have been configured successfully.")


def main() -> None:
    """
    Initializes and starts the Telegram bot application with persistence and job queue.
    """
    if not BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN is missing from environment variables!")
        return

    # Setup persistence
    persistence = PicklePersistence(filepath="market_watcher_data.pickle")

    # Build the application and hook the post_init function
    application = (
        Application.builder()
        .token(BOT_TOKEN)
        .persistence(persistence)
        .post_init(post_init)
        .build()
    )

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