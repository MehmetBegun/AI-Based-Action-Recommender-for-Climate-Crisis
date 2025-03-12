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
        "https://ekolojihaber.com/feed/",
        "https://www.greenpeace.org/turkiye/rss/",
        "https://www.wwf.org.tr/rss",
        "https://www.yesilbasin.org/rss",
        "https://www.cevredergisi.com/rss"
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
        0: İklim Değişikliği,
        1: Enerji,
        2: Biyoçeşitlilik,
        3: Kirlilik,
        4: Küresel Isınma,
        5: Doğal Afetler,
        6: Tarım ve Gıda Güvenliği,
        7: Su Kaynakları,
        8: Hava Kirliliği,
        9: Atık Yönetimi,
        10: Sürdürülebilir Kalkınma,
        11: Çevre Eğitimi,
        12: Yenilenebilir Enerji,
        13: Ormanlar ve Ağaçlandırma,
        14: Plastik Kirliliği,
        15: Ekosistem Koruma,
        16: Çevresel Adalet,
        17: Çevre Hukuku,
        18: Karbon Salınımı,
        19: Sera Gazları,
        20: Deniz Kirliliği,
        21: Karasal Biyoçeşitlilik,
        22: Tükenebilir Doğal Kaynaklar,
        23: Geri Dönüşüm,
        24: Çevresel Etki Değerlendirmesi,
        25: Çevre Dostu Ulaşım,
        26: Sıfır Atık Hareketi,
        27: Yeşil Teknolojiler,
        28: Karbon Ayak İzi,
        29: Çevresel Yıkımın Ekonomik Etkileri,
        30: Toprak Kirliliği
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
    "İklim Değişikliği: Karbon ayak izinizi azaltmak için toplu taşıma kullanın, enerji tasarrufu yapın, yenilenebilir enerji kaynaklarını tercih edin, çevre dostu ürünler kullanın."
    "Enerji: Enerji tasarrufu sağlayan cihazlar kullanın, güneş ve rüzgar enerjisi gibi yenilenebilir enerji kaynaklarına yatırım yapın, enerji verimliliği yüksek ampuller kullanın."
    "Biyoçeşitlilik: Yerel ağaçlandırma projelerine destek olun, doğal yaşam alanlarını korumaya yönelik projelere katılın, zararlı kimyasallar içermeyen ürünler kullanın."
    "Kirlilik: Plastik kullanımını azaltın, geri dönüşüm yapın, çevreye zarar vermeyen temizlik ürünleri kullanın, sürdürülebilir moda ve tüketim alışkanlıklarını benimseyin."
    "Küresel Isınma: Karbon salınımını azaltmaya yönelik adımlar atın, yenilenebilir enerji kullanın, enerji tasarrufu sağlayan ürünler tercih edin."
    "Doğal Afetler: Afetlere hazırlıklı olun, afet anında çevreyi koruyan çözümler geliştirin, afet bölgelerinde yardım projelerine katılın."
    "Tarım ve Gıda Güvenliği: Organik tarım yöntemlerini destekleyin, yerel ürünler tüketin, gıda israfını azaltın."
    "Su Kaynakları: Su tasarrufu sağlamak için verimli kullanım alışkanlıkları geliştirin, suyu kirletmemek için çevre dostu temizlik ürünleri kullanın."
    "Hava Kirliliği: Araç kullanımı yerine bisiklet veya yürüyüş gibi alternatif ulaşım yöntemlerini tercih edin, yeşil alanları artırmaya yönelik projelere katılın."
    "Atık Yönetimi: Geri dönüşüm yapın, atıkları azaltın, composting yöntemleriyle organik atıkları değerlendirin."
    "Sürdürülebilir Kalkınma: Sürdürülebilir üretim ve tüketim alışkanlıkları geliştirin, çevre dostu iş uygulamalarını teşvik edin."
    "Çevre Eğitimi: Çevre bilincini artıran etkinliklere katılın, çevre dostu davranışları öğretmek için eğitimler düzenleyin."
    "Yenilenebilir Enerji: Yenilenebilir enerji kaynakları kullanın, güneş panelleri veya rüzgar türbinleri gibi alternatif enerji sistemlerine yatırım yapın."
    "Ormanlar ve Ağaçlandırma: Ağaç dikme etkinliklerine katılın, ormanları koruyan ve sürdüren projelere destek olun."
    "Plastik Kirliliği: Tek kullanımlık plastiklerden kaçının, plastik yerine sürdürülebilir malzemelerden üretilen ürünleri tercih edin."
    "Ekosistem Koruma: Doğal yaşam alanlarını koruyacak projelere destek olun, ekosistem restorasyon çalışmaları yapın."
    "Çevresel Adalet: Çevreye duyarlı yaşam tarzını destekleyin, çevre kirliliğinden en çok etkilenen topluluklarla dayanışma içinde olun."
    "Çevre Hukuku: Çevre dostu yasaların uygulanmasını destekleyin, çevreyi koruyan hukuki düzenlemelere katılın."
    "Karbon Salınımı: Karbon salınımını azaltmaya yönelik bireysel ve toplumsal önlemler alın, karbon ayak izinizi izleyin."
    "Sera Gazları: Sera gazı salınımını azaltmak için temiz enerji kullanın, enerji verimliliğini artıracak önlemler uygulayın."
    "Karasal Alanların Korunması: Ormanlar, çöller ve diğer karasal alanları korumak için koruma projelerine katılın, sürdürülebilir tarım yöntemlerini destekleyin."
    "Deniz Kirliliği: Denizleri korumak için plaj temizliği etkinliklerine katılın, deniz kirliliğini önlemeye yönelik projelere destek olun."
    "Çevre Dostu Ulaşım: Elektrikli araçlar kullanın, toplu taşıma sistemlerini tercih edin, bisiklet yolları oluşturulmasına destek verin."
    "Geri Dönüşüm: Atıkları geri dönüştürün, geri dönüşüm farkındalığı yaratacak etkinlikler düzenleyin."
    "Tüketim Alışkanlıkları: Gereksiz tüketimi azaltın, sürdürülebilir ve yerel üretilen ürünleri tercih edin, minimalizmi benimseyin."
    "Yerel Ekonomiler ve Çevre: Yerel üreticileri destekleyin, çevre dostu yerel ürünleri tercih edin."
    "Sıfır Atık Hareketi: Atık üretimini sıfırlamak için ürünleri tekrar kullanın, gereksiz ambalajlardan kaçının."
    "Çevre Dostu Üretim: Çevre dostu üretim süreçlerini tercih edin, doğal kaynakları verimli kullanın."
    "Toprak Kirliliği: Toprağı kirleten kimyasalların kullanımını azaltın, sürdürülebilir tarım yöntemleri uygulayın."
    "Küresel Çevre Politikaları: Küresel çevre anlaşmalarına destek olun, çevre politikalarına katılım sağlayarak daha yeşil bir dünya için çalışın."
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
