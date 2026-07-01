import json
import os
import logging

logger = logging.getLogger(__name__)

TRANSLATIONS = {}

def load_translations() -> None:
    """Loads all JSON dictionary files from the locales directory."""
    locales_dir = "locales"
    if not os.path.exists(locales_dir):
        os.makedirs(locales_dir)
        
    for lang in ["en", "fa"]:
        file_path = os.path.join(locales_dir, f"{lang}.json")
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                TRANSLATIONS[lang] = json.load(f)
        else:
            TRANSLATIONS[lang] = {}
            logger.warning(f"Translation file not found: {file_path}")

def get_text(lang: str, key: str, **kwargs) -> str:
    """
    Retrieves the translated text for a given key and language.
    Falls back to English if the key is missing in the target language.
    Automatically applies Right-to-Left Mark (RLM) for Persian text.
    """
    if lang not in TRANSLATIONS:
        lang = "en"
        
    text = TRANSLATIONS.get(lang, {}).get(key)
    
    # Fallback to English if key does not exist in selected language
    if not text:
        text = TRANSLATIONS.get("en", {}).get(key, key)
        
    if kwargs:
        text = text.format(**kwargs)
        
    # Apply Unicode Right-to-Left Mark (RLM) to force correct BiDi rendering
    if lang == "fa":
        text = f"\u200F{text}\u200F"
        
    return text

# Initialize translations on module load
load_translations()