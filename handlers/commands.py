from telegram import Update
from telegram.ext import ContextTypes


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