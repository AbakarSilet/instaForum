import requests

LIBRETRANSLATE_URL = "https://libretranslate.com/translate"  # Assure-toi que l'URL de l'API est correcte

def translate_text(text, source_lang, target_lang):
    payload = {
        'q': text,
        'source': source_lang,
        'target': target_lang,
        'format': 'text'
    }
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.post(LIBRETRANSLATE_URL, json=payload, headers=headers)
    
    if response.status_code == 200:
        return response.json()['translatedText']
    else:
        raise Exception(f"Error in translation: {response.status_code} {response.text}")
