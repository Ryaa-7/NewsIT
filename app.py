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

CATEGORY_ICONS = {"AI": "🤖", "Software": "💻", "Kesehatan": "🩺", "Finance": "💰"}
CATEGORY_COLORS = {"AI": "#E30513", "Software": "#0A5FBF", "Kesehatan": "#0A8F5C", "Finance": "#B8860B"}

# ---------------------------------------------------------------------------
# CSS ALA PORTAL BERITA (terinspirasi tata letak Kompas.com)
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
    .main { background-color: #f4f4f4; }
    .topbar {
        background-color: #E30513;
        color: white;
        padding: 10px 20px;
        font-size: 13px;
        font-weight: 600;
        letter-spacing: 0.5px;
        margin-bottom: 0px;
    }
    .brand-title {
        font-family: Georgia, 'Times New Roman', serif;
        font-weight: 900;
        font-size: 42px;
        color: #111;
        margin: 10px 0 0 0;
        letter-spacing: -1px;
    }
    .brand-sub {
        color: #555;
        font-size: 14px;
        margin-bottom: 10px;
    }
    .hero-card {
        background-color: white;
        border-radius: 6px;
        padding: 18px;
        border-left: 5px solid #E30513;
        margin-bottom: 8px;
    }
    .hero-tag {
        background-color: #E30513;
        color: white;
        font-size: 11px;
        font-weight: 700;
        padding: 2px 8px;
        border-radius: 3px;
        letter-spacing: 0.5px;
    }
    .hero-headline {
        font-family: Georgia, 'Times New Roman', serif;
        font-size: 24px;
        font-weight: 800;
        color: #111;
        margin: 8px 0 4px 0;
        line-height: 1.25;
    }
    .news-card {
        background-color: white;
        border-radius: 6px;
        padding: 14px;
        margin-bottom: 12px;
        border: 1px solid #e5e5e5;
        transition: 0.15s;
    }
    .news-tag {
        color: white;
        font-size: 10px;
        font-weight: 700;
        padding: 2px 7px;
        border-radius: 3px;
        letter-spacing: 0.5px;
    }
    .news-title {
        font-family: Georgia, 'Times New Roman', serif;
        font-size: 16px;
        font-weight: 700;
        color: #111;
        margin: 6px 0 4px 0;
        line-height: 1.3;
    }
    .news-meta {
        color: #888;
        font-size: 11px;
    }
    .trending-item {
        display: flex;
        align-items: flex-start;
        padding: 10px 0;
        border-bottom: 1px solid #eee;
    }
    .trending-number {
        font-family: Georgia, serif;
        font-size: 26px;
        font-weight: 900;
        color: #E30513;
        width: 34px;
        flex-shrink: 0;
    }
    .trending-text {
        font-size: 14px;
        font-weight: 600;
        color: #111;
        line-height: 1.3;
    }
    .live-dot {
        height: 8px; width: 8px;
        background-color: #E30513;
        border-radius: 50%;
        display: inline-block;
        margin-right: 6px;
        animation: pulse 1.5s infinite;
    }
    @keyframes pulse {
        0% { opacity: 1; } 50% { opacity: 0.3; } 100% { opacity: 1; }
    }
    a { text-decoration: none !important; color: inherit !important; }
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
    color = CATEGORY_COLORS.get(art["category"], "#E30513")
    title_size = "20px" if big else "16px"
    st.markdown(
        f"""
        <a href="{art['link']}" target="_blank">
        <div class="news-card">
            <span class="news-tag" style="background-color:{color}">{art['category'].upper()}</span>
            <div class="news-title" style="font-size:{title_size}">{art['title']}</div>
            <div class="news-meta">📰 {art['source']} &nbsp;·&nbsp; 🕒 {art['published'] or 'baru saja'}</div>
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
# HEADER ALA PORTAL BERITA
# ---------------------------------------------------------------------------
st.markdown(
    '<div class="topbar">🔴 LIVE UPDATE &nbsp;|&nbsp; AI · SOFTWARE · KESEHATAN · FINANCE &nbsp;|&nbsp; '
    + datetime.now().strftime("%A, %d %B %Y — %H:%M") + '</div>',
    unsafe_allow_html=True,
)
st.markdown('<div class="brand-title">TECH RADAR</div>', unsafe_allow_html=True)
st.markdown('<div class="brand-sub">Portal informasi teknologi, kesehatan & finansial terkini — diperbarui otomatis tiap menit</div>', unsafe_allow_html=True)

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
        color = CATEGORY_COLORS.get(headline["category"], "#E30513")
        st.markdown(
            f"""
            <a href="{headline['link']}" target="_blank">
            <div class="hero-card">
                <span class="hero-tag" style="background-color:{color}">🔥 HEADLINE · {headline['category'].upper()}</span>
                <div class="hero-headline">{headline['title']}</div>
                <div class="news-meta">📰 {headline['source']} &nbsp;·&nbsp; 🕒 {headline['published'] or 'baru saja'}</div>
            </div>
            </a>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("#### 📌 Berita Terbaru")
    for art in sorted_articles[1:9]:
        render_card(art)

with col_side:
    st.markdown("#### 🔥 Trending Dunia")
    with st.container(border=True):
        for i, art in enumerate(sorted_articles[:8], start=1):
            st.markdown(
                f"""
                <a href="{art['link']}" target="_blank">
                <div class="trending-item">
                    <div class="trending-number">{i}</div>
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
    st.markdown(f"#### 🔎 Hasil pencarian: \"{custom_query}\"")
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
                        <span class="news-tag" style="background-color:#555">NEWSAPI</span>
                        <div class="news-title">{a.get('title','')}</div>
                        <div class="news-meta">📰 {a.get('source',{}).get('name','')}</div>
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
