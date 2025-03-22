import sqlite3

def cleanup_duplicates():
    conn = sqlite3.connect("news.db")
    cur = conn.cursor()

    # Aynı linke sahip kayıtların en küçük id'lisini tut, diğerlerini sil
    cur.execute("""
        DELETE FROM news
        WHERE id NOT IN (
            SELECT MIN(id)
            FROM news
            GROUP BY link
        )
    """)
    conn.commit()
    conn.close()
    print("✔️ Tekrarlayan haberler silindi.")

if __name__ == "__main__":
    cleanup_duplicates()
