import re
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils.scraper import fetch_price
from utils.i18n import get_text

# Define a standard regex pattern for validating HTTP/HTTPS URLs
URL_PATTERN = re.compile(
    r"^(?:http)s?://"
    r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|"
    r"localhost|"
    r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"
    r"(?::\d+)?"
    r"(?:/?|[/?]\S+)$", re.IGNORECASE
)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handles incoming text messages, menu button clicks, and user states.
    Dynamically supports multi-language buttons and responses.
    """
    user_text = update.message.text #type: ignore
    user_data = context.user_data
    
    # Get the user's selected language (default to English if not set)
    lang = user_data.get("language", "en") #type: ignore

    # 1. Action for "Add New Link" (Checks both English and Persian button text)
    if user_text in [get_text("en", "btn_add"), get_text("fa", "btn_add")]:
        user_data["state"] = "AWAITING_LINK" #type: ignore
        await update.message.reply_text(text=get_text(lang, "ask_link")) #type: ignore
        
    # 2. Action for "My Links" (Checks both English and Persian button text)
    elif user_text in [get_text("en", "btn_list"), get_text("fa", "btn_list")]:
        links = user_data.get("links", []) #type: ignore
        
        if not links:
            # Displays translated message indicating the tracking list is empty
            await update.message.reply_text(text=get_text(lang, "empty_list")) #type: ignore
            return
            
        await update.message.reply_text(text=get_text(lang, "list_header")) #type: ignore
        
        # Loop through each link and send it with a unique "Delete" inline button
        for index, item in enumerate(links):
            url = item["url"]
            last_price = item["last_price_text"]
            
            # Truncate long URLs just for clean appearance in chat
            display_url = url if len(url) < 40 else url[:37] + "..."
            
            keyboard = [[InlineKeyboardButton(get_text(lang, "btn_delete"), callback_data=f"delete_{index}")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # If last_price is a dictionary from the new scraper, extract the raw price
            price_display = last_price.get("price", "") if isinstance(last_price, dict) else last_price
            
            msg_text = get_text(lang, "status_text", url=display_url, price=price_display)
            await update.message.reply_text(text=msg_text, reply_markup=reply_markup) #type: ignore
            
    # 3. Action for "Help" (Checks both English and Persian button text)
    elif user_text in [get_text("en", "btn_help"), get_text("fa", "btn_help")]:
        await update.message.reply_text(text=get_text(lang, "help_text")) #type: ignore

    # 4. Action when waiting for a URL link
    elif user_data.get("state") == "AWAITING_LINK": #type: ignore
        if URL_PATTERN.match(user_text): #type: ignore
            product_link = user_text
            user_data["state"] = None #type: ignore
            
            if "links" not in user_data: #type: ignore
                user_data["links"] = [] #type: ignore
                
            if any(item["url"] == product_link for item in user_data["links"]): #type: ignore
                await update.message.reply_text(text=get_text(lang, "already_tracked")) #type: ignore
                return
            
            processing_msg = await update.message.reply_text(text=get_text(lang, "extracting")) #type: ignore
            
            # Call our async scraper (which now returns a dictionary)
            result = await fetch_price(product_link) #type: ignore
            
            if result.get("success"):
                price_value = result.get("price")
                user_data["links"].append({ #type: ignore
                    "url": product_link,
                    "last_price_text": result
                })
                
                success_text = get_text(lang, "add_success", url=product_link, price=price_value)
                await processing_msg.edit_text(text=success_text)
            else:
                error_key = result.get("error_key", "err_connection")
                await processing_msg.edit_text(text=get_text(lang, error_key))
        else:
            await update.message.reply_text(text=get_text(lang, "invalid_url")) #type: ignore
            
    else:
        # Default translated response for unhandled text messages
        await update.message.reply_text(text=get_text(lang, "use_menu")) #type: ignore