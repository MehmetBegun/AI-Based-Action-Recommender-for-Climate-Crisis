import sqlite3

DB_PATH = "news.db"

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
    """Haberleri veritabanına ekler."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    for news in news_list:
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
