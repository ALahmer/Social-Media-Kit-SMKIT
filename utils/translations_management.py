from utils.env_management import load_from_env
import logging
import sys


env_data = load_from_env()


def get_translation(key: str, language: str, **kwargs) -> str:
    """
    Retrieves the translation for a given key and language.

    Args:
        key (str): The key representing the text to translate.
        language (str): The target language (e.g., 'en', 'it').
        kwargs: Any placeholders needed for formatting the string.

    Returns:
        str: The translated text.
    """
    translations = env_data.get("translations_dictionary", {})
    lang_translations = translations.get(language, {})
    translation = lang_translations.get(key, None)

    if not translation:
        if language != 'en':
            logging.warning(
                f"Translation for '{key}' in '{language}' language not found. Falling back to 'en' language translation.")
            return get_translation(key, 'en', **kwargs)
        else:
            logging.error(f"Translation for '{key}' not populated in '{language}' language.")
            sys.exit(1)

    return translation.format(**kwargs)
