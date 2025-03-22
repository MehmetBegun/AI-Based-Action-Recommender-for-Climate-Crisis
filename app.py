from flask import Flask, render_template
from modules.db_helper import init_db
from modules.rss_scraper import fetch_rss
from modules.lda_categorizer import categorize_news
from modules.suggestions import action_suggestions
from modules.manuel_entry import add_manual_news 
import sqlite3
from flask import request, redirect, url_for
from modules.web_scraper import fetch_iklim_haber, fetch_wwf

app = Flask(__name__, template_folder="templates")

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

@app.route("/admin", methods=["GET", "POST"])
def admin_panel():
    if request.method == "POST":
        title = request.form.get("title")
        link = request.form.get("link")
        summary = request.form.get("summary")
        add_manual_news(title, link, summary)
        return redirect(url_for("home"))
    return render_template("admin.html")
print("------------------------------------------")
print(app.url_map)

if __name__ == "__main__":
    init_db()
    fetch_rss()
    categorize_news()
    app.run(debug=True)
