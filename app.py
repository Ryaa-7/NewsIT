"""
Tech Radar — Portal Berita Teknologi Real-Time (gaya portal berita)
Menampilkan berita terbaru & trending seputar AI, Software, Kesehatan, dan Finance.
Auto-update tiap 60 detik.

Cara jalankan:
    pip install -r requirements.txt
    streamlit run app.py
"""

import streamlit as st
import feedparser
import requests
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from streamlit_autorefresh import st_autorefresh

# ---------------------------------------------------------------------------
# KONFIGURASI HALAMAN
# ---------------------------------------------------------------------------
st.set_page_config(page_title="Tech Radar", page_icon="🛰️", layout="wide")

REFRESH_SECONDS = 60  # cache & auto-refresh tiap 1 menit

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

CATEGORY_ICONS = {"AI": "AI", "Software": "SOFTWARE", "Kesehatan": "KESEHATAN", "Finance": "FINANCE"}
ACCENT = "#B8151F"  # merah gelap tunggal, dipakai sangat minim — bukan warna dominan

# ---------------------------------------------------------------------------
# CSS ALA EDITORIAL MINIMALIS (terinspirasi tata letak kompas.id)
# Prinsip: putih bersih, tipografi serif, garis tipis sebagai pemisah,
# nyaris tanpa warna kecuali aksen merah gelap yang sangat terbatas.
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
    html, body, .stApp, .main, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        background-color: #FFFFFF !important;
        color: #1a1a1a !important;
    }
    [data-testid="stSidebar"] {
        background-color: #FAFAFA !important;
        border-right: 1px solid #e2e2e2;
    }
    .masthead {
        text-align: center;
        padding: 28px 0 14px 0;
        border-bottom: 3px solid #1a1a1a;
    }
    .masthead-title {
        font-family: Georgia, 'Times New Roman', serif;
        font-weight: 900;
        font-size: 48px;
        color: #1a1a1a;
        letter-spacing: -0.5px;
        margin: 0;
    }
    .masthead-sub {
        font-family: Georgia, serif;
        font-style: italic;
        color: #6b6b6b;
        font-size: 13px;
        margin-top: 4px;
    }
    .navbar {
        display: flex;
        justify-content: center;
        gap: 28px;
        padding: 10px 0;
        border-bottom: 1px solid #e2e2e2;
        margin-bottom: 26px;
        font-family: Arial, sans-serif;
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 1px;
        color: #444;
    }
    .navbar span.active { color: #B8151F; border-bottom: 2px solid #B8151F; padding-bottom: 8px; }
    .eyebrow {
        font-family: Arial, sans-serif;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 1.2px;
        color: #B8151F;
        text-transform: uppercase;
    }
    .hero-headline {
        font-family: Georgia, 'Times New Roman', serif;
        font-size: 30px;
        font-weight: 700;
        color: #1a1a1a;
        line-height: 1.2;
        margin: 8px 0 10px 0;
    }
    .hero-block {
        border-bottom: 1px solid #e2e2e2;
        padding-bottom: 22px;
        margin-bottom: 22px;
    }
    .news-card {
        padding: 0 0 16px 0;
        margin-bottom: 16px;
        border-bottom: 1px solid #ececec;
    }
    .news-title {
        font-family: Georgia, 'Times New Roman', serif;
        font-size: 17px;
        font-weight: 700;
        color: #1a1a1a;
        margin: 5px 0 5px 0;
        line-height: 1.32;
    }
    .news-meta {
        color: #8a8a8a;
        font-family: Arial, sans-serif;
        font-size: 11px;
    }
    .section-heading {
        font-family: Georgia, serif;
        font-size: 15px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: #1a1a1a;
        border-bottom: 2px solid #1a1a1a;
        padding-bottom: 6px;
        margin-bottom: 14px;
    }
    .trending-item {
        display: flex;
        align-items: flex-start;
        padding: 12px 0;
        border-bottom: 1px solid #ececec;
    }
    .trending-number {
        font-family: Georgia, serif;
        font-size: 22px;
        font-weight: 400;
        color: #c9c9c9;
        width: 30px;
        flex-shrink: 0;
    }
    .trending-text {
        font-family: Georgia, serif;
        font-size: 14px;
        font-weight: 700;
        color: #1a1a1a;
        line-height: 1.3;
    }
    .live-dot {
        height: 7px; width: 7px;
        background-color: #B8151F;
        border-radius: 50%;
        display: inline-block;
        margin-right: 6px;
        animation: pulse 1.5s infinite;
    }
    @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.25; } 100% { opacity: 1; } }
    a { text-decoration: none !important; color: inherit !important; }
    hr { border-color: #e2e2e2 !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# FUNGSI AMBIL & OLAH DATA
# ---------------------------------------------------------------------------
@st.cache_data(ttl=REFRESH_SECONDS, show_spinner=False)
def fetch_rss(url: str, source_name: str, category: str):
    try:
        feed = feedparser.parse(url)
        articles = []
        for entry in feed.entries[:8]:
            published_raw = entry.get("published", entry.get("updated", ""))
            published_dt = None
            try:
                published_dt = parsedate_to_datetime(published_raw)
            except Exception:
                published_dt = None
            articles.append(
                {
                    "title": entry.get("title", "(tanpa judul)"),
                    "link": entry.get("link", "#"),
                    "summary": (entry.get("summary", "") or "")[:200],
                    "published": published_raw,
                    "published_dt": published_dt,
                    "source": source_name,
                    "category": category,
                }
            )
        return articles
    except Exception as e:
        return [{"error": str(e), "source": source_name, "category": category}]


@st.cache_data(ttl=REFRESH_SECONDS, show_spinner=False)
def fetch_all():
    """Ambil semua kategori sekaligus, dipakai untuk hero & trending."""
    all_articles = []
    for category, sources in RSS_FEEDS.items():
        for source_name, url in sources.items():
            all_articles.extend(fetch_rss(url, source_name, category))
    return [a for a in all_articles if "error" not in a]


def sort_recent(articles):
    with_date = [a for a in articles if a["published_dt"] is not None]
    without_date = [a for a in articles if a["published_dt"] is None]
    with_date.sort(key=lambda a: a["published_dt"], reverse=True)
    return with_date + without_date


def render_card(art, big=False):
    title_size = "20px" if big else "17px"
    st.markdown(
        f"""
        <a href="{art['link']}" target="_blank">
        <div class="news-card">
            <span class="eyebrow">{art['category']}</span>
            <div class="news-title" style="font-size:{title_size}">{art['title']}</div>
            <div class="news-meta">{art['source']} &nbsp;·&nbsp; {art['published'] or 'baru saja'}</div>
        </div>
        </a>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# AUTO-REFRESH TIAP 60 DETIK
# ---------------------------------------------------------------------------
st_autorefresh(interval=REFRESH_SECONDS * 1000, key="auto_refresh")

# ---------------------------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------------------------
st.sidebar.title("⚙️ Pengaturan")
st.sidebar.markdown('<span class="live-dot"></span> **LIVE** — update tiap 60 detik', unsafe_allow_html=True)

use_newsapi = st.sidebar.toggle("Gunakan NewsAPI.org (opsional)", value=False)
newsapi_key, custom_query = "", ""
if use_newsapi:
    st.sidebar.info("Daftar API key gratis di https://newsapi.org")
    newsapi_key = st.sidebar.text_input("NewsAPI Key", type="password")
    custom_query = st.sidebar.text_input("Kata kunci pencarian", value="artificial intelligence")

if st.sidebar.button("🔄 Refresh manual"):
    st.cache_data.clear()
    st.rerun()

st.sidebar.caption(f"Terakhir dimuat: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")

# ---------------------------------------------------------------------------
# MASTHEAD ALA EDITORIAL (terinspirasi kompas.id: bersih, serif, minim warna)
# ---------------------------------------------------------------------------
st.markdown(
    f"""
    <div class="masthead">
        <div class="masthead-title">TECH RADAR</div>
        <div class="masthead-sub">{datetime.now().strftime("%A, %d %B %Y")} &nbsp;—&nbsp;
        <span class="live-dot"></span>diperbarui otomatis tiap menit</div>
    </div>
    <div class="navbar">
        <span class="active">BERANDA</span>
        <span>AI</span>
        <span>SOFTWARE</span>
        <span>KESEHATAN</span>
        <span>FINANCE</span>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.spinner("Memuat berita terbaru..."):
    all_articles = fetch_all()

sorted_articles = sort_recent(all_articles)

# ---------------------------------------------------------------------------
# HERO + TRENDING (layout 2 kolom ala homepage portal berita)
# ---------------------------------------------------------------------------
col_main, col_side = st.columns([2.2, 1])

with col_main:
    if sorted_articles:
        headline = sorted_articles[0]
        st.markdown(
            f"""
            <a href="{headline['link']}" target="_blank">
            <div class="hero-block">
                <span class="eyebrow">Headline &middot; {headline['category']}</span>
                <div class="hero-headline">{headline['title']}</div>
                <div class="news-meta">{headline['source']} &nbsp;·&nbsp; {headline['published'] or 'baru saja'}</div>
            </div>
            </a>
            """,
            unsafe_allow_html=True,
        )

    st.markdown('<div class="section-heading">Berita Terbaru</div>', unsafe_allow_html=True)
    for art in sorted_articles[1:9]:
        render_card(art)

with col_side:
    st.markdown('<div class="section-heading">Terpopuler</div>', unsafe_allow_html=True)
    for i, art in enumerate(sorted_articles[:8], start=1):
        st.markdown(
            f"""
            <a href="{art['link']}" target="_blank">
            <div class="trending-item">
                <div class="trending-number">{i:02d}</div>
                <div class="trending-text">{art['title']}
                    <div class="news-meta">{art['category']} · {art['source']}</div>
                </div>
            </div>
            </a>
            """,
            unsafe_allow_html=True,
        )

# ---------------------------------------------------------------------------
# HASIL PENCARIAN NEWSAPI (kalau aktif)
# ---------------------------------------------------------------------------
if use_newsapi and newsapi_key:
    st.divider()
    st.markdown(f'<div class="section-heading">Hasil Pencarian: "{custom_query}"</div>', unsafe_allow_html=True)
    try:
        resp = requests.get(
            "https://newsapi.org/v2/everything",
            params={"q": custom_query, "sortBy": "publishedAt", "language": "id", "pageSize": 6, "apiKey": newsapi_key},
            timeout=10,
        )
        data = resp.json()
        if data.get("status") == "ok":
            cols = st.columns(3)
            for i, a in enumerate(data.get("articles", [])[:6]):
                with cols[i % 3]:
                    st.markdown(
                        f"""<div class="news-card">
                        <span class="eyebrow">NewsAPI</span>
                        <div class="news-title">{a.get('title','')}</div>
                        <div class="news-meta">{a.get('source',{}).get('name','')}</div>
                        </div>""",
                        unsafe_allow_html=True,
                    )
        else:
            st.warning(data.get("message", "Gagal ambil data NewsAPI"))
    except Exception as e:
        st.warning(f"Gagal ambil data NewsAPI: {e}")

# ---------------------------------------------------------------------------
# GRID PER KATEGORI (bagian bawah, gaya section homepage)
# ---------------------------------------------------------------------------
st.divider()
tabs = st.tabs([f"{CATEGORY_ICONS[cat]} {cat}" for cat in RSS_FEEDS.keys()])

for tab, category in zip(tabs, RSS_FEEDS.keys()):
    with tab:
        cat_articles = sort_recent([a for a in all_articles if a["category"] == category])
        if not cat_articles:
            st.info("Tidak ada artikel ditemukan untuk kategori ini saat ini.")
        else:
            cols = st.columns(3)
            for i, art in enumerate(cat_articles):
                with cols[i % 3]:
                    render_card(art)

st.divider()
st.caption(
    "Sumber: RSS feed resmi tiap kategori. Halaman auto-refresh tiap 60 detik. "
    "Kalau satu sumber gagal dimuat, sumber lain tetap tampil normal."
)
