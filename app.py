import os
import feedparser
import sqlite3
from bs4 import BeautifulSoup
import nltk
from nltk.corpus import stopwords
import re
from flask import Flask, render_template
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation

# NLTK Stopwords İndirme
nltk.download('stopwords')
stop_words = set(stopwords.words('turkish'))

# RSS Kaynağı
RSS_URL = "https://www.theguardian.com/environment/climate-crisis/rss"

def clean_text(text):
    text = BeautifulSoup(text, "html.parser").get_text()  # HTML etiketlerini kaldır
    text = text.lower()  # Küçük harfe çevir
    text = re.sub(r'[^a-zA-Z0-9ğüşıöçĞÜŞİÖÇ\s.,!?]', '', text)  # Türkçe karakterler korunarak sadece gereksiz semboller kaldırılır
    tokens = text.split()
    return " ".join(tokens[:150])  # Maksimum 100 kelime al (haberin tamamını göstermemek için)


# RSS Verisini Çek ve Veritabanına Kaydet
def fetch_rss():
    rss_feeds = [
        "https://yesilgazete.org/feed/",
    ]

    conn = sqlite3.connect("news.db")
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS news")
    cur.execute("""
        CREATE TABLE news (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            link TEXT,
            summary TEXT,
            category TEXT
        )
    """)

    total_news = 0
    for rss_url in rss_feeds:
        try:
            feed = feedparser.parse(rss_url)
            for entry in feed.entries:
                title = entry.title
                link = entry.link
                summary = clean_text(entry.description)
                cur.execute("INSERT INTO news (title, link, summary, category) VALUES (?, ?, ?, ?)",
                            (title, link, summary, None))
                total_news += 1
        except Exception as e:
            print(f"RSS kaynağı alınırken hata oluştu ({rss_url}): {e}")

    conn.commit()
    conn.close()
    print(f"{total_news} haber çekildi ve veritabanına kaydedildi.")


# Makine Öğrenmesi ile Kategorize Etme
def categorize_news():
    conn = sqlite3.connect("news.db")
    cur = conn.cursor()
    cur.execute("SELECT id, summary FROM news")
    rows = cur.fetchall()
    conn.close()
    
    corpus = [row[1] for row in rows]
    
    count_vectorizer = CountVectorizer(max_df=0.8, min_df=2, stop_words=list(stop_words))  # Türkçe stopwords eklendi
    X_counts = count_vectorizer.fit_transform(corpus)
    
    lda_model = LatentDirichletAllocation(n_components=4, random_state=42)
    lda_model.fit(X_counts)
    
    doc_topics = lda_model.transform(X_counts)
    topic_labels = {
        0: "İklim Değişikliği",
        1: "Enerji",
        2: "Biyoçeşitlilik",
        3: "Kirlilik"
    }
    
    conn = sqlite3.connect("news.db")
    cur = conn.cursor()
    for idx, row in enumerate(rows):
        top_topic = doc_topics[idx].argmax()
        category = topic_labels.get(top_topic, "Genel")
        cur.execute("UPDATE news SET category = ? WHERE id = ?", (category, row[0]))
    conn.commit()
    conn.close()
    print("Haberler kategorilere ayrıldı ve veritabanı güncellendi.")


# Flask Web Uygulaması
app = Flask(__name__)

action_suggestions = {
    "İklim Değişikliği": "Karbon ayak izinizi azaltmak için toplu taşıma kullanın, enerji tasarrufu yapın, yenilenebilir enerji kaynaklarını tercih edin, çevre dostu ürünler kullanın.",
    "Enerji": "Enerji tasarrufu sağlayan cihazlar kullanın, güneş ve rüzgar enerjisi gibi yenilenebilir enerji kaynaklarına yatırım yapın, enerji verimliliği yüksek ampuller kullanın.",
    "Biyoçeşitlilik": "Yerel ağaçlandırma projelerine destek olun, doğal yaşam alanlarını korumaya yönelik projelere katılın, zararlı kimyasallar içermeyen ürünler kullanın.",
    "Kirlilik": "Plastik kullanımını azaltın, geri dönüşüm yapın, çevreye zarar vermeyen temizlik ürünleri kullanın, sürdürülebilir moda ve tüketim alışkanlıklarını benimseyin.",
    "Genel": "Çevreyi korumak için sürdürülebilir alışkanlıklar edinin. Küçük adımlarla büyük farklar yaratabilirsiniz. Toplumda çevre bilincini artırmak için çevre dostu etkinliklere katılın."
}

@app.route("/")
def home():
    conn = sqlite3.connect("news.db")
    cur = conn.cursor()
    cur.execute("SELECT title, link, summary, category FROM news")
    rows = cur.fetchall()
    conn.close()
    
    articles = []
    for title, link, summary, category in rows:
        if category is None:
            category = "Genel"
        suggestion = action_suggestions.get(category, action_suggestions["Genel"])
        articles.append({
            "title": title,
            "link": link,
            "summary": summary,
            "category": category,
            "suggestion": suggestion
        })
    return render_template("index.html", articles=articles)

if __name__ == "__main__":
    try:
        fetch_rss()
        categorize_news()
    except Exception as e:
        print(f"Hata oluştu: {e}")
    app.run(debug=True)
