import os
import csv
import streamlit as st

@st.cache_data
def load_translations(lang_code: str) -> dict:
    """
    Loads the translation dictionary from the specified CSV file.
    Caches the result in memory to prevent repetitive disk reads.
    
    Args:
        lang_code (str): The language code (e.g., 'es', 'fr').
        
    Returns:
        dict: A dictionary mapping English base strings to translated strings.
    """
    translations = {}
    file_path = f"translations/{lang_code}.csv"
    
    if os.path.exists(file_path):
        with open(file_path, mode='r', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader, None)  # Skip the header row (key, value)
            for row in reader:
                if len(row) >= 2:
                    translations[row[0]] = row[1]
    else:
        print(f"⚠️ Translation file not found: {file_path}")
        
    return translations

def _(text: str, *args) -> str:
    """
    Translates a given string based on the current session language.
    Applies string formatting if positional arguments are provided.
    
    Usage:
        _("Welcome back, {0}!", "Admin")
        _("Added {0} items to {1}", 50, "Choluteca")
        
    Args:
        text (str): The base string in English (acts as the translation key).
        *args: Variable length argument list for string formatting.
        
    Returns:
        str: The translated and formatted string.
    """
    # Default to English ('en') if no language is set in the session
    current_lang = st.session_state.get('language', 'en')
    
    # If the target language is English, the base text IS the translation
    if current_lang == 'en':
        translated_text = text
    else:
        dict_translations = load_translations(current_lang)
        translated_text = dict_translations.get(text, text)
    
    # Apply string formatting if arguments are provided
    if args:
        try:
            # Supports both unpacked args: _("Msg", arg1, arg2) 
            # and list/tuple args: _("Msg", [arg1, arg2])
            if len(args) == 1 and isinstance(args[0], (list, tuple)):
                translated_text = translated_text.format(*args[0])
            else:
                translated_text = translated_text.format(*args)
        except Exception as e:
            print(f"Formatting error in translation key '{text}': {e}")
            
    return translated_text