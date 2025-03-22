from modules.text_cleaner import clean_text
from modules.db_helper import insert_news
from modules.lda_categorizer import categorize_news

def add_manual_news(title, link, summary):
    """Kullanıcıdan gelen haber verisini işler, veritabanına ekler ve kategorize eder."""
    cleaned_summary = clean_text(summary)
    news_data = [{
        "title": title,
        "link": link,
        "summary": cleaned_summary,
        "category": None
    }]
    insert_news(news_data)

    # Eklenen haberi kategorize et
    categorize_news()


#başlık:	Avrupa’da Yenilenebilir Enerji Kullanımı Rekor Kırdı
#link: https://example.com/yenilenebilir-enerji-avrupa
#özet: Avrupa ülkeleri, fosil yakıt tüketimini azaltmak amacıyla 2024'te yenilenebilir enerji kullanımında rekor seviyelere ulaştı. Güneş ve rüzgar enerjisi, enerji üretiminin %60’ını oluşturdu.