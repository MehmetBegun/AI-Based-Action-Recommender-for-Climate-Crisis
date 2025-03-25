import requests
from bs4 import BeautifulSoup
import re
from modules.db_helper import insert_news, is_news_exist
from modules.text_cleaner import clean_text

def fetch_iklim_haber():
    url = "https://www.iklimhaber.org/"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    news_list = []

    # Ana haber kutuları
    articles = soup.find_all("article", class_="herald-fa-item")

    for article in articles:
        try:
            title_tag = article.find("h2", class_="entry-title")
            link_tag = title_tag.find("a") if title_tag else None
            summary_tag = article.find("div", class_="entry-content")
            summary_p = summary_tag.find("p") if summary_tag else None

            if not link_tag:
                continue

            title = link_tag.text.strip()
            link = link_tag["href"]
            summary = summary_p.text.strip() if summary_p else ""

            if len(summary.split()) < 5:
                detail_response = requests.get(link)
                detail_soup = BeautifulSoup(detail_response.content, "html.parser")
                detail_paragraphs = detail_soup.find_all("p")
                if detail_paragraphs:
                    detail_text = " ".join(p.get_text() for p in detail_paragraphs)
                    sentences = re.split(r'(?<=[.!?]) +', detail_text)
                    summary = " ".join(sentences[:2])
                else:
                    summary = ""

            if not is_news_exist(link):
                news_list.append({
                    "title": title,
                    "link": link,
                    "summary": clean_text(summary),
                    "category": None
                })
        except Exception as e:
            print("Ana haber hatası:", e)
            continue

    # 🆕 Öne çıkanlar / diğer kutular (sadece görsel + link var)
    thumbnails = soup.find_all("div", class_="herald-post-thumbnail herald-format-icon-middle")
    
    for thumb in thumbnails:
        try:
            a_tag = thumb.find("a")
            if not a_tag:
                continue
            link = a_tag["href"]
            title = a_tag.get("title", "").strip()

            # Detaydan içerik çek (özet)
            detail_response = requests.get(link)
            detail_soup = BeautifulSoup(detail_response.content, "html.parser")
            detail_paragraphs = detail_soup.find_all("p")

            if detail_paragraphs:
                detail_text = " ".join([p.get_text() for p in detail_paragraphs])
                sentences = re.split(r'(?<=[.!?]) +', detail_text)
                summary = " ".join(sentences[:2])
            else:
                summary = ""

            if not is_news_exist(link):
                news_list.append({
                    "title": title,
                    "link": link,
                    "summary": clean_text(summary),
                    "category": None
                })

        except Exception as e:
            print("Öne çıkan haber hatası:", e)
            continue

    insert_news(news_list)
    print(f"✔️ {len(news_list)} haber başarıyla kaydedildi.")
