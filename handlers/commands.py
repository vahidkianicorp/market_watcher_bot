from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handles the /start command. Sends a welcoming message to the user
    along with a persistent main menu keyboard.
    """
    user_first_name = update.effective_user.first_name # type: ignore

    # Define the keyboard layout with emojis for better UI
    keyboard = [
        [KeyboardButton("➕ Add New Link")],
        [KeyboardButton("📋 My Links"), KeyboardButton("ℹ️ Help")]
    ]

    # Create the reply markup, resizing it for better mobile view
    reply_markup = ReplyKeyboardMarkup(
        keyboard, 
        resize_keyboard=True, 
        input_field_placeholder="Choose an option..."
    )

    welcome_message = (
        f"Hello {user_first_name}! 👋\n"
        f"Welcome to Market Watcher Bot.\n"
        f"Please choose an option from the menu below."
    )

    await update.message.reply_text( # type: ignore
        text=welcome_message,
        reply_markup=reply_markup
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handles the /help command. Provides a guide to the user.
    """
    help_text = (
        "🤖 Market Watcher Bot Help:\n\n"
        "Use the menu below to navigate.\n"
        "If you want to track a product, click on '➕ Add New Link'."
    )
    
    await update.message.reply_text(text=help_text) # type: ignore