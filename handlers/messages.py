import re
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
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
    """
    user_text = update.message.text #type: ignore
    user_data = context.user_data

    # 1. Action for "Add New Link"
    if user_text == "➕ Add New Link":
        user_data["state"] = "AWAITING_LINK" #type: ignore
        await update.message.reply_text( #type: ignore
            text="Please send me the valid product URL link you want to track."
        )
        
    # 2. Action for "My Links"
    elif user_text == "📋 My Links":
        links = user_data.get("links", []) #type: ignore
        
        if not links:
            await update.message.reply_text("ℹ️ Your tracking list is currently empty.") #type: ignore
            return
            
        await update.message.reply_text("📋 **Your Tracked Products:**") #type: ignore
        
        # Loop through each link and send it with a unique "Delete" inline button
        for index, item in enumerate(links):
            url = item["url"]
            last_price = item["last_price_text"]
            
            # Truncate long URLs just for clean appearance in chat
            display_url = url if len(url) < 40 else url[:37] + "..."
            
            # The callback_data will look like "delete_0", "delete_1", etc.
            keyboard = [[InlineKeyboardButton("❌ Delete from List", callback_data=f"delete_{index}")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            msg_text = f"🔗 Link: {display_url}\n\nStatus: {last_price}"
            await update.message.reply_text(text=msg_text, reply_markup=reply_markup) #type: ignore
            
    # 3. Action for "Help"
    elif user_text == "ℹ️ Help":
        help_text = (
            "🤖 Market Watcher Bot Help:\n\n"
            "Use the menu below to navigate.\n"
            "• '➕ Add New Link' to track a new product.\n"
            "• '📋 My Links' to see and manage your list."
        )
        await update.message.reply_text(text=help_text) #type: ignore

    # 4. Action when waiting for a URL link
    elif user_data.get("state") == "AWAITING_LINK": #type: ignore
        if URL_PATTERN.match(user_text): #type: ignore
            product_link = user_text
            user_data["state"] = None #type: ignore
            
            if "links" not in user_data: #type: ignore
                user_data["links"] = [] #type: ignore
                
            if any(item["url"] == product_link for item in user_data["links"]): #type: ignore
                await update.message.reply_text("⚠️ You are already tracking this product!") #type: ignore
                return
            
            processing_msg = await update.message.reply_text("⏳ Extracting data, please wait...") #type: ignore
            result_text = await fetch_price(product_link) #type: ignore
            
            user_data["links"].append({ #type: ignore
                "url": product_link,
                "last_price_text": result_text
            })
            
            await processing_msg.edit_text(
                text=(
                    f"Successfully added to your tracking list! 🎯\n\n"
                    f"Link: {product_link}\n\n"
                    f"{result_text}"
                )
            )
        else:
            await update.message.reply_text( #type: ignore
                text="❌ Invalid URL format! Please send a valid internet link."
            )
            
    else:
        await update.message.reply_text(text="Please use the menu buttons to navigate options.") #type: ignore