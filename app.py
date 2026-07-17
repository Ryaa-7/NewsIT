"""
Dashboard Teknologi Real-Time
Menampilkan berita terbaru seputar AI, Software, Kesehatan, dan Finance
menggunakan RSS feed (gratis, tanpa API key) dan opsional NewsAPI.org
(kalau kamu punya API key sendiri, hasil pencarian bisa lebih luas dan bisa custom keyword).

Cara jalankan:
    pip install -r requirements.txt
    streamlit run app.py
"""

import streamlit as st
import feedparser
import requests
from datetime import datetime, timezone
import time

# ---------------------------------------------------------------------------
# KONFIGURASI HALAMAN
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Tech Radar",
    page_icon="🛰️",
    layout="wide",
)

REFRESH_SECONDS = 15 * 60  # cache tiap 15 menit dianggap "real-time" wajar untuk RSS

# ---------------------------------------------------------------------------
# SUMBER RSS PER KATEGORI (semua gratis, tanpa API key)
# ---------------------------------------------------------------------------
RSS_FEEDS = {
    "AI": {
        "TechCrunch AI": "https://techcrunch.com/category/artificial-intelligence/feed/",
        "MIT Technology Review": "https://www.technologyreview.com/feed/",
        "VentureBeat AI": "https://venturebeat.com/category/ai/feed/",
    },
    "Software": {
        "TechCrunch": "https://techcrunch.com/feed/",
        "Ars Technica": "https://feeds.arstechnica.com/arstechnica/index",
        "The Verge": "https://www.theverge.com/rss/index.xml",
    },
    "Kesehatan": {
        "Reuters Health": "https://www.reuters.com/arc/outboundfeeds/rss/category/health/?outputType=xml",
        "Healthline News": "https://www.healthline.com/rss/health-news",
        "WHO News": "https://www.who.int/rss-feeds/news-english.xml",
    },
    "Finance": {
        "Reuters Business": "https://www.reuters.com/arc/outboundfeeds/rss/category/business/?outputType=xml",
        "CNBC Finance": "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=10000664",
        "Investing.com": "https://www.investing.com/rss/news.rss",
    },
}

CATEGORY_ICONS = {"AI": "🤖", "Software": "💻", "Kesehatan": "🩺", "Finance": "💰"}


# ---------------------------------------------------------------------------
# FUNGSI AMBIL DATA (di-cache supaya tidak fetch berulang tiap interaksi UI)
# ---------------------------------------------------------------------------
@st.cache_data(ttl=REFRESH_SECONDS, show_spinner=False)
def fetch_rss(url: str, source_name: str):
    """Ambil dan parse satu RSS feed. Return list of dict artikel."""
    try:
        feed = feedparser.parse(url)
        articles = []
        for entry in feed.entries[:8]:
            published = entry.get("published", entry.get("updated", ""))
            articles.append(
                {
                    "title": entry.get("title", "(tanpa judul)"),
                    "link": entry.get("link", "#"),
                    "summary": entry.get("summary", "")[:220],
                    "published": published,
                    "source": source_name,
                }
            )
        return articles
    except Exception as e:
        return [{"error": str(e), "source": source_name}]


@st.cache_data(ttl=REFRESH_SECONDS, show_spinner=False)
def fetch_newsapi(query: str, api_key: str):
    """Ambil berita dari NewsAPI.org (butuh API key gratis dari newsapi.org)."""
    try:
        url = "https://newsapi.org/v2/everything"
        params = {
            "q": query,
            "sortBy": "publishedAt",
            "language": "id",
            "pageSize": 10,
            "apiKey": api_key,
        }
        resp = requests.get(url, params=params, timeout=10)
        data = resp.json()
        if data.get("status") != "ok":
            return [{"error": data.get("message", "Gagal ambil data NewsAPI")}]
        articles = []
        for a in data.get("articles", []):
            articles.append(
                {
                    "title": a.get("title", "(tanpa judul)"),
                    "link": a.get("url", "#"),
                    "summary": (a.get("description") or "")[:220],
                    "published": a.get("publishedAt", ""),
                    "source": a.get("source", {}).get("name", "NewsAPI"),
                }
            )
        return articles
    except Exception as e:
        return [{"error": str(e)}]


def render_articles(articles):
    if not articles:
        st.info("Tidak ada artikel ditemukan.")
        return
    for art in articles:
        if "error" in art:
            st.warning(f"Gagal ambil dari {art.get('source', 'sumber ini')}: {art['error']}")
            continue
        with st.container(border=True):
            st.markdown(f"**[{art['title']}]({art['link']})**")
            cols = st.columns([3, 1])
            with cols[0]:
                if art["summary"]:
                    st.caption(art["summary"] + "...")
            with cols[1]:
                st.caption(f"📰 {art['source']}")
                if art["published"]:
                    st.caption(f"🕒 {art['published']}")


# ---------------------------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------------------------
st.sidebar.title("⚙️ Pengaturan")
st.sidebar.caption(
    "Data diambil dari RSS feed sumber resmi tiap kategori. "
    "Cache diperbarui otomatis tiap 15 menit."
)

use_newsapi = st.sidebar.toggle("Gunakan NewsAPI.org (opsional)", value=False)
newsapi_key = ""
custom_query = ""
if use_newsapi:
    st.sidebar.info(
        "Daftar API key gratis di https://newsapi.org lalu tempel di bawah. "
        "Cocok kalau kamu mau cari topik spesifik, bukan cuma kategori umum."
    )
    newsapi_key = st.sidebar.text_input("NewsAPI Key", type="password")
    custom_query = st.sidebar.text_input("Kata kunci pencarian", value="artificial intelligence")

if st.sidebar.button("🔄 Refresh sekarang"):
    st.cache_data.clear()
    st.rerun()

st.sidebar.caption(f"Terakhir dimuat: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")

# ---------------------------------------------------------------------------
# HALAMAN UTAMA
# ---------------------------------------------------------------------------
st.title("🛰️ Tech Radar")
st.caption("Update terbaru seputar AI, Software, Kesehatan, dan Finance dalam satu tempat.")

if use_newsapi and newsapi_key:
    st.subheader(f"🔎 Hasil pencarian NewsAPI: \"{custom_query}\"")
    with st.spinner("Mengambil data..."):
        results = fetch_newsapi(custom_query, newsapi_key)
    render_articles(results)
    st.divider()

tabs = st.tabs([f"{CATEGORY_ICONS[cat]} {cat}" for cat in RSS_FEEDS.keys()])

for tab, category in zip(tabs, RSS_FEEDS.keys()):
    with tab:
        st.subheader(f"{CATEGORY_ICONS[category]} {category}")
        all_articles = []
        with st.spinner(f"Memuat berita {category}..."):
            for source_name, url in RSS_FEEDS[category].items():
                all_articles.extend(fetch_rss(url, source_name))

        # urutkan yang ada tanggalnya paling atas (best-effort, format tanggal RSS bervariasi)
        render_articles(all_articles)

st.divider()
st.caption(
    "Catatan: kalau salah satu sumber RSS gagal dimuat (server sumber down/berubah struktur), "
    "sumber lain di kategori yang sama tetap tampil. Ganti URL feed di RSS_FEEDS kalau ada yang mati."
)
