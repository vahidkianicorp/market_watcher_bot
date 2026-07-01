from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes
from utils.i18n import get_text


def get_main_menu_keyboard(lang: str) -> ReplyKeyboardMarkup:
    """Generates the main menu keyboard based on the user's selected language."""
    keyboard = [
        [KeyboardButton(get_text(lang, "btn_add"))],
        [KeyboardButton(get_text(lang, "btn_list")), KeyboardButton(get_text(lang, "btn_help"))]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, input_field_placeholder="...")


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handles the /start command. Sends a welcoming message to the user
    along with a persistent main menu keyboard.
    """
    user_data = context.user_data #type: ignore

    # Trigger language selection if it has not been set yet
    if "language" not in user_data: #type: ignore
        keyboard = [
            [
                InlineKeyboardButton(get_text("en", "btn_en"), callback_data="setlang_en"),
                InlineKeyboardButton(get_text("fa", "btn_fa"), callback_data="setlang_fa")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Dual-language instruction for the very first interaction
        await update.message.reply_text( #type: ignore
            text="Please choose your language:\nلطفاً زبان خود را انتخاب کنید:",
            reply_markup=reply_markup
        )
        return
    
    # Normal startup if language is already configured
    lang = user_data["language"] #type: ignore
    user_first_name = update.effective_user.first_name #type: ignore
    welcome_message = get_text(lang, "welcome", name=user_first_name)

    await update.message.reply_text( #type: ignore
        text=welcome_message,
        reply_markup=get_main_menu_keyboard(lang)
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handles the /help command. Provides a guide to the user.
    """
    lang = context.user_data.get("language", "en") #type: ignore
    await update.message.reply_text(text=get_text(lang, "help_text")) #type: ignore