# Backend/Translator.py
import requests
from gtts import gTTS
import os

def translate_text(text, target_language='en'):
    """
    Translate text and optionally speak the result using gTTS
    
    Args:
        text: Text to translate
        target_language: Target language name or code
    
    Returns:
        Translated text or error message
    """
    try:
        lang_map = {
            'french': 'fr',
            'spanish': 'es',
            'german': 'de',
            'japanese': 'ja',
            'chinese': 'zh',
            'hindi': 'hi',
            'english': 'en',
            'arabic': 'ar',
            'russian': 'ru',
            'portuguese': 'pt',
            'korean': 'ko',
            'urdu': 'ur'
        }

        lang_code = lang_map.get(target_language.lower(), target_language.lower())

        url = "https://libretranslate.com/translate"
        payload = {
            'q': text,
            'source': 'auto',
            'target': lang_code,
            'format': 'text'
        }
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()

        translated_text = response.json().get('translatedText', '')

        if translated_text:
            try:
                # Convert text to speech
                tts = gTTS(text=translated_text, lang=lang_code)
                tts.save("translated_audio.mp3")
                os.system("start translated_audio.mp3")  # For Windows
                return translated_text
            except Exception as e:
                return f"Translation: {translated_text} (Audio failed: {e})"
        else:
            return "Translation not available"

    except requests.exceptions.RequestException as e:
        return f"Translation service unavailable: {str(e)}"
    except Exception as e:
        return f"Translation error: {str(e)}"
