import logging
from telegram import Update
from telegram.ext import ContextTypes

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
                
                logger.info(f"User {update.effective_user.id} deleted link index {index_to_delete}") #type: ignore
                
                # Edit the message to show it was successfully deleted
                await query.edit_message_text( #type: ignore
                    text=f"🗑️ Product successfully removed from your list!\n\nLink: {removed_item['url']}"
                )
            else:
                await query.edit_message_text(text="⚠️ This item could not be found or was already deleted.") #type: ignore
                
        except (IndexError, ValueError) as e:
            logger.error(f"Error executing callback delete action: {e}")
            await query.edit_message_text(text="❌ An error occurred while trying to remove this item.") #type: ignore