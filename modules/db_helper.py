import sqlite3
from modules.language_filter import is_kurdish  # Dil tespiti için eklenen modül

DB_PATH = "news.db"

# Yasaklı başlıklar listesi
EXCLUDED_TITLES = [
    "Di Çemê Dîcleyê de mirina bi komî ya masiyan",
    "Li dijî projeya çêkirina bendavê dê pêvjaoya hiqûqî bê destpêkirin"
]

def init_db():
    """Veritabanını başlatır ve tabloyu oluşturur."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS news (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT,
                    link TEXT,
                    summary TEXT,
                    category TEXT)""")
    conn.commit()
    conn.close()

def insert_news(news_list):
    """Haberleri veritabanına ekler. Yasaklı başlıklar veya Kürtçe haberler eklenmez."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    for news in news_list:
        # Önce, haber başlığının blacklist'te olup olmadığını kontrol ediyoruz.
        if news["title"] in EXCLUDED_TITLES:
            print("Blacklist'te olan başlık atlandı:", news["title"])
            continue

        # Daha sonra, dil tespitiyle kontrol edelim (hem başlık hem özet üzerinden)
        if is_kurdish(news["title"]) or is_kurdish(news["summary"]):
            print("Dil filtresiyle atlandı:", news["title"])
            continue

        cur.execute("INSERT INTO news (title, link, summary, category) VALUES (?, ?, ?, ?)",
                    (news["title"], news["link"], news["summary"], news["category"]))
    conn.commit()
    conn.close()

def is_news_exist(link):
    """Belirli bir linke sahip haber veritabanında var mı kontrol eder."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM news WHERE link = ?", (link,))
    result = cur.fetchone()
    conn.close()
    return result is not None
