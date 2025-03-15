import feedparser
from modules.db_helper import insert_news
from modules.text_cleaner import clean_text

RSS_FEEDS = [
    "https://yesilgazete.org/feed/",
    "https://ekolojihaber.com/feed/",
    "https://www.greenpeace.org/turkiye/rss/",
    "https://www.wwf.org.tr/rss"
]

def fetch_rss():
    """RSS haberlerini çeker ve veritabanına kaydeder."""
    news_list = []
    for rss_url in RSS_FEEDS:
        try:
            feed = feedparser.parse(rss_url)
            for entry in feed.entries:
                news_list.append({
                    "title": entry.title,
                    "link": entry.link,
                    "summary": clean_text(entry.description),
                    "category": None
                })
        except Exception as e:
            print(f"Hata: {e}")

    insert_news(news_list)
