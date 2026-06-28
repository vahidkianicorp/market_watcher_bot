from telegram import Update
from telegram.ext import ContextTypes


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handles incoming text messages, menu button clicks, and user states.
    """
    user_text = update.message.text
    user_data = context.user_data

    # Check if the user clicked the "Add New Link" button
    if user_text == "➕ Add New Link":
        # Set the user state to remember they are supposed to send a link next
        user_data["state"] = "AWAITING_LINK"
        await update.message.reply_text(
            text="Please send me the valid product URL link you want to track."
        )
        
    # Check if the user is currently expected to send a link
    elif user_data.get("state") == "AWAITING_LINK":
        product_link = user_text
        # Clear the state so subsequent messages aren't treated as links
        user_data["state"] = None
        
        # In future phases, we will add URL validation and scraping logic here
        await update.message.reply_text(
            text=(
                f"Successfully received! 🎯\n\n"
                f"I will start tracking this link:\n{product_link}"
            )
        )
        
    else:
        # Default response for unhandled text messages
        await update.message.reply_text(
            text="Please use the menu buttons to navigate options."
        )