"""Multi-language translation support."""

TRANSLATION_BACKEND = "none"

try:
    from googletrans import Translator
    TRANSLATOR_AVAILABLE = True
    TRANSLATION_BACKEND = "googletrans"
except Exception:
    TRANSLATOR_AVAILABLE = False

if not TRANSLATOR_AVAILABLE:
    try:
        from deep_translator import GoogleTranslator as DeepGoogleTranslator
        TRANSLATOR_AVAILABLE = True
        TRANSLATION_BACKEND = "deep-translator"
    except Exception:
        TRANSLATOR_AVAILABLE = False

# Supported languages
SUPPORTED_LANGUAGES = {
    "en": "English",
    "hi": "Hindi",
    "de": "German",
    "fr": "French",
    "es": "Spanish",
    "zh-cn": "Chinese (Simplified)",
}


def is_available():
    """Check if translation is available."""
    return TRANSLATOR_AVAILABLE


def translate_text(text: str, target_language: str) -> tuple:
    """
    Translate text to target language.
    
    Args:
        text: Text to translate
        target_language: Target language code (e.g., 'hi', 'de', 'fr')
    
    Returns:
        (translated_text, error_message)
    """
    if not TRANSLATOR_AVAILABLE:
        return None, "Translation backend not installed. Run: pip install deep-translator"

    if target_language == "en":
        # No need to translate to English
        return text, None

    if target_language not in SUPPORTED_LANGUAGES:
        return None, f"Unsupported language. Supported: {', '.join(SUPPORTED_LANGUAGES.values())}"

    try:
        if TRANSLATION_BACKEND == "googletrans":
            translator = Translator()
            translation = translator.translate(text, src="en", dest=target_language)
            return translation.text, None

        if TRANSLATION_BACKEND == "deep-translator":
            translated = DeepGoogleTranslator(source="en", target=target_language).translate(text)
            return translated, None

        return None, "No translation backend available"
    except Exception as e:
        return None, f"Translation error: {str(e)}"


def get_language_name(lang_code: str) -> str:
    """Get language name from language code."""
    return SUPPORTED_LANGUAGES.get(lang_code, "Unknown")


def list_languages() -> dict:
    """Return all supported languages."""
    return SUPPORTED_LANGUAGES


def translate_result(result: dict, target_language: str) -> dict:
    """
    Translate an entire result dictionary.
    
    Args:
        result: Result dict with 'text' and 'score' keys
        target_language: Target language code
    
    Returns:
        Updated result dict with translated text
    """
    if target_language == "en" or not TRANSLATOR_AVAILABLE:
        return result

    translated_text, error = translate_text(result.get("text", ""), target_language)

    if error:
        result["translation_error"] = error
    else:
        result["translated_text"] = translated_text

    return result
