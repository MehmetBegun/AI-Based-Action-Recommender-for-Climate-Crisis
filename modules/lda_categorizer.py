import sqlite3
import re
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from modules.text_cleaner import clean_text
from modules.suggestions import topic_labels, topic_keywords

def categorize_news():
    conn = sqlite3.connect("news.db")
    cur = conn.cursor()
    cur.execute("SELECT id, summary FROM news WHERE summary IS NOT NULL")
    rows = cur.fetchall()

    if not rows:
        print("Hiç haber bulunamadı.")
        return

    ids = [row[0] for row in rows]
    summaries = [row[1] for row in rows]

    vectorizer = CountVectorizer(max_df=0.8, min_df=2, stop_words=None)
    X_counts = vectorizer.fit_transform(summaries)

    lda_model = LatentDirichletAllocation(n_components=8, random_state=42)
    lda_model.fit(X_counts)

    doc_topics = lda_model.transform(X_counts)

    threshold = 0.3  # LDA eşik değeri

    for idx, summary in enumerate(summaries):
        assigned_categories = set()
        summary_clean = clean_text(summary)

        # Anahtar kelimelerle eşleşme kontrolü
        for category, keywords in topic_keywords.items():
            if any(re.search(r"\b" + re.escape(keyword), summary_clean) for keyword in keywords):
                assigned_categories.add(category)

        # Eğer hiç kategori bulunamazsa, LDA'yı deneyelim
        if len(assigned_categories) == 0:
            topic_dist = doc_topics[idx]
            top_indices = topic_dist.argsort()[::-1]

            # Eşik değer kontrolü yapalım
            for i in top_indices:
                if topic_dist[i] >= threshold:
                    assigned_categories.add(topic_labels.get(i, "Genel"))
                    if len(assigned_categories) >= 2:
                        break

        # Son kategori ataması (tek veya çift veya hiç yok)
        if len(assigned_categories) == 0:
            category_str = "Eşleşme Yok"
        else:
            category_str = ", ".join(list(assigned_categories)[:2])

        cur.execute("UPDATE news SET category = ? WHERE id = ?", (category_str, ids[idx]))

    conn.commit()
    conn.close()
    print("✔️ Her haber için kategori atandı.")
