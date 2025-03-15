import sqlite3
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from modules.text_cleaner import clean_text
from modules.suggestions import topic_labels

def categorize_news():
    """LDA modeli ile haberleri kategorilere ayırır."""
    conn = sqlite3.connect("news.db")
    cur = conn.cursor()
    cur.execute("SELECT id, summary FROM news")
    rows = cur.fetchall()
    conn.close()
    
    corpus = [row[1] for row in rows]

    vectorizer = CountVectorizer(max_df=0.8, min_df=2)
    X_counts = vectorizer.fit_transform(corpus)

    lda_model = LatentDirichletAllocation(n_components=4, random_state=42)
    lda_model.fit(X_counts)
    
    doc_topics = lda_model.transform(X_counts)
    
    conn = sqlite3.connect("news.db")
    cur = conn.cursor()
    for idx, row in enumerate(rows):
        top_topic = doc_topics[idx].argmax()
        category = topic_labels.get(top_topic, "Genel")
        cur.execute("UPDATE news SET category = ? WHERE id = ?", (category, row[0]))
    conn.commit()
    conn.close()
