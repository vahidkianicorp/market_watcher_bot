import logging
from telegram.ext import ContextTypes
from utils.scraper import fetch_price

logger = logging.getLogger(__name__)

async def check_prices_job(context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Background job to iterate through all saved links across all users,
    check for price updates, and notify the user if a change occurs.
    """
    # context.application.user_data contains a dictionary of all users' data
    all_users_data = context.application.user_data
    
    for user_id, user_data in all_users_data.items():
        links = user_data.get("links", [])
        
        for item in links:
            url = item["url"]
            old_price_text = item["last_price_text"]
            
            try:
                new_price_text = await fetch_price(url)
                
                # Check if price exists and has changed
                if "✅" in new_price_text and new_price_text != old_price_text:
                    item["last_price_text"] = new_price_text
                    
                    notification_msg = (
                        f"🔔 Price Update Alert!\n\n"
                        f"Link: {url}\n\n"
                        f"Previous: {old_price_text}\n"
                        f"New: {new_price_text}"
                    )
                    await context.bot.send_message(chat_id=user_id, text=notification_msg)
                    
            except Exception as e:
                logger.error(f"Failed to check price for {url}: {e}")