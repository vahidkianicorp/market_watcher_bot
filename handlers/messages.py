import re
from telegram import Update
from telegram.ext import ContextTypes

# Import our new scraping module
from utils.scraper import fetch_price

# Define a standard regex pattern for validating HTTP/HTTPS URLs
URL_PATTERN = re.compile(
    r"^(?:http)s?://" # Matches http:// or https://
    r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|" # domain
    r"localhost|" # localhost
    r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})" # or ip
    r"(?::\d+)?" # optional port
    r"(?:/?|[/?]\S+)$", re.IGNORECASE
)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handles incoming text messages, menu button clicks, and user states.
    Validates user input against a URL pattern before accepting it.
    """
    user_text = update.message.text # type: ignore
    user_data = context.user_data

    # Check if the user clicked the "Add New Link" button
    if user_text == "➕ Add New Link":
        user_data["state"] = "AWAITING_LINK" # type: ignore
        await update.message.reply_text( # type: ignore
            text="Please send me the valid product URL link you want to track."
        )
        
    # Check if the user is currently expected to send a link
    elif user_data.get("state") == "AWAITING_LINK": # type: ignore
        
        # Validate the input against the Regex pattern
        if URL_PATTERN.match(user_text): # type: ignore
            product_link = user_text
            
            # Clear the state only if the validation passes
            user_data["state"] = None # type: ignore

            # Send a loading message so the user knows we are processing
            processing_msg = await update.message.reply_text("⏳ Extracting data, please wait...") # type: ignore
            
            # Call our async scraper
            result_text = await fetch_price(product_link) # type: ignore
            
            # Edit the processing message with the final result
            await processing_msg.edit_text(
                text=(
                    f"Link: {product_link}\n\n"
                    f"{result_text}"
                )
            )
        else:
            # If invalid, keep the state as "AWAITING_LINK" and ask again
            await update.message.reply_text( # type: ignore
                text=(
                    "❌ Invalid URL format!\n"
                    "Please send a valid internet link (e.g., https://example.com)."
                )
            )
            
    else:
        # Default response for unhandled text messages
        await update.message.reply_text( # type: ignore
            text="Please use the menu buttons to navigate options."
        )