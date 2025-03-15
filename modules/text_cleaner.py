import re
from bs4 import BeautifulSoup
import nltk
from nltk.corpus import stopwords

nltk.download('stopwords')
stop_words = set(stopwords.words('turkish'))

def clean_text(text):
    """HTML etiketlerini kaldırır, küçük harfe çevirir ve stopwords temizler."""
    if not isinstance(text, str):
        return ""
    
    text = BeautifulSoup(text, "html.parser").get_text()
    text = text.lower()
    text = re.sub(r'[^a-zA-Z0-9ğüşıöçĞÜŞİÖÇ\s.,!?]', '', text)
    tokens = text.split()
    tokens = [word for word in tokens if word not in stop_words]
    return " ".join(tokens[:150])
