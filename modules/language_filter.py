from langdetect import detect, DetectorFactory
DetectorFactory.seed = 0

def is_kurdish(text):
    """
    Metnin Kürtçe olup olmadığını belirlemek için önce langdetect,
    eğer sonuç güvenilir değilse ek anahtar kelime kontrolü yapar.
    """
    try:
        lang = detect(text)
        if lang == 'ku':
            return True
    except Exception:
        pass

    # Ek olarak belirgin Kürtçe kelimeler
    kurdish_keywords = ["dîcleyê", "komî", "çemê", "mirina", "bi komî"]
    text_lower = text.lower()
    for keyword in kurdish_keywords:
        if keyword in text_lower:
            return True
    return False
