import logging
from telegram import Update
from telegram.ext import ContextTypes
from utils.i18n import get_text
from handlers.commands import get_main_menu_keyboard

logger = logging.getLogger(__name__)

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Processes actions triggered by inline keyboard buttons (Callback Queries).
    Handles product deletion from the user tracking list.
    """
    query = update.callback_query
    # Acknowledge the click immediately to stop the loading animation on the button
    await query.answer() #type: ignore
    
    data = query.data #type: ignore
    user_data = context.user_data

    # Handle Language Selection
    if data.startswith("setlang_"): #type: ignore
        selected_lang = data.split("_")[1] #type: ignore
        user_data["language"] = selected_lang #type: ignore

        await query.message.delete() #type: ignore
        
        user_first_name = update.effective_user.first_name #type: ignore
        welcome_message = get_text(selected_lang, "welcome", name=user_first_name)
        
        await context.bot.send_message(
            chat_id=update.effective_chat.id, #type: ignore
            text=welcome_message,
            reply_markup=get_main_menu_keyboard(selected_lang)
        )
        return

    # Handle Link Deletion
    lang = user_data.get("language", "en") #type: ignore
    links = user_data.get("links", []) #type: ignore
    
    if data.startswith("delete_"): #type: ignore
        try:
            # Extract the index number from strings like "delete_3"
            index_to_delete = int(data.split("_")[1]) #type: ignore
            
            if 0 <= index_to_delete < len(links):
                # Remove the item from the list
                removed_item = links.pop(index_to_delete)
                # Mark persistence as modified so ptb knows it needs to re-save to the pickle file
                user_data["links"] = links #type: ignore
                
                success_text = get_text(lang, "del_success", url=removed_item["url"])
                await query.edit_message_text(text=success_text) #type: ignore
            else:
                await query.edit_message_text(text=get_text(lang, "del_not_found")) #type: ignore
                
        except (IndexError, ValueError) as e:
            logger.error(f"Callback deletion error: {e}")
            await query.edit_message_text(text=get_text(lang, "del_error")) #type: ignore