"""
Tech Radar — Portal Berita Teknologi Real-Time (gaya Kompas.com: berwarna, ramai, bergambar)
Menampilkan berita terbaru & trending seputar AI, Software, Kesehatan, dan Finance.
Auto-update tiap 60 detik.

Cara jalankan:
    pip install -r requirements.txt
    streamlit run app.py
"""

import re
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
CATEGORY_COLORS = {"AI": "#E30513", "Software": "#0A5FBF", "Kesehatan": "#0A8F5C", "Finance": "#D9A404"}
CATEGORY_GRADIENT = {
    "AI": "linear-gradient(135deg,#E30513,#8B0000)",
    "Software": "linear-gradient(135deg,#0A5FBF,#003C7A)",
    "Kesehatan": "linear-gradient(135deg,#0A8F5C,#065A38)",
    "Finance": "linear-gradient(135deg,#D9A404,#8A6900)",
}

# ---------------------------------------------------------------------------
# CSS ALA PORTAL BERITA BERWARNA (terinspirasi tata letak Kompas.com)
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
    html, body, .stApp, [data-testid="stAppViewContainer"] {
        background-color: #F0F2F5 !important;
    }
    [data-testid="stSidebar"] { background-color: #FFFFFF !important; }
    .topbar {
        background: linear-gradient(90deg,#E30513,#B8151F);
        color: white;
        padding: 10px 22px;
        border-radius: 8px;
        font-size: 13px;
        font-weight: 700;
        letter-spacing: 0.4px;
        margin-bottom: 14px;
        box-shadow: 0 3px 10px rgba(227,5,19,0.25);
    }
    .brand-title {
        font-family: Georgia, 'Times New Roman', serif;
        font-weight: 900;
        font-size: 46px;
        background: linear-gradient(90deg,#E30513,#0A5FBF);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 6px 0 0 0;
        letter-spacing: -1px;
    }
    .brand-sub { color: #555; font-size: 14px; margin-bottom: 16px; }
    .hero-card {
        position: relative;
        border-radius: 14px;
        overflow: hidden;
        margin-bottom: 10px;
        box-shadow: 0 6px 20px rgba(0,0,0,0.12);
        color: white;
        min-height: 260px;
        display: flex;
        align-items: flex-end;
        background-size: cover;
        background-position: center;
    }
    .hero-overlay {
        width: 100%;
        padding: 22px;
        background: linear-gradient(180deg, rgba(0,0,0,0) 0%, rgba(0,0,0,0.85) 100%);
    }
    .hero-tag {
        color: white;
        font-size: 11px;
        font-weight: 800;
        padding: 4px 10px;
        border-radius: 20px;
        letter-spacing: 0.5px;
        display: inline-block;
        margin-bottom: 8px;
    }
    .hero-headline {
        font-family: Georgia, 'Times New Roman', serif;
        font-size: 26px;
        font-weight: 800;
        color: white;
        margin: 4px 0 6px 0;
        line-height: 1.25;
        text-shadow: 0 2px 6px rgba(0,0,0,0.5);
    }
    .hero-meta { color: #eee; font-size: 12px; }
    .news-card {
        background-color: white;
        border-radius: 12px;
        overflow: hidden;
        margin-bottom: 16px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.07);
        transition: transform 0.15s, box-shadow 0.15s;
    }
    .news-card:hover { transform: translateY(-3px); box-shadow: 0 8px 18px rgba(0,0,0,0.14); }
    .news-img {
        width: 100%;
        height: 140px;
        background-size: cover;
        background-position: center;
    }
    .news-body { padding: 12px 14px 14px 14px; }
    .news-tag {
        color: white;
        font-size: 10px;
        font-weight: 800;
        padding: 3px 9px;
        border-radius: 20px;
        letter-spacing: 0.5px;
        display: inline-block;
    }
    .news-title {
        font-family: Georgia, 'Times New Roman', serif;
        font-size: 16px;
        font-weight: 700;
        color: #171717;
        margin: 8px 0 6px 0;
        line-height: 1.32;
    }
    .news-meta { color: #999; font-size: 11px; }
    .trending-panel {
        background: white;
        border-radius: 12px;
        padding: 4px 16px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.07);
    }
    .trending-heading {
        font-family: Georgia, serif;
        font-weight: 800;
        font-size: 16px;
        color: #171717;
        padding: 14px 0 10px 0;
        border-bottom: 3px solid #E30513;
        margin-bottom: 4px;
    }
    .trending-item {
        display: flex;
        align-items: flex-start;
        gap: 10px;
        padding: 12px 0;
        border-bottom: 1px solid #f0f0f0;
    }
    .trending-number {
        font-family: Georgia, serif;
        font-size: 26px;
        font-weight: 900;
        -webkit-text-stroke: 1.4px #E30513;
        color: white;
        width: 30px;
        flex-shrink: 0;
    }
    .trending-text { font-size: 13.5px; font-weight: 700; color: #171717; line-height: 1.3; }
    .section-heading {
        font-family: Georgia, serif;
        font-weight: 800;
        font-size: 19px;
        color: #171717;
        margin: 6px 0 14px 0;
        border-left: 5px solid #E30513;
        padding-left: 10px;
    }
    .live-dot {
        height: 8px; width: 8px;
        background-color: white;
        border-radius: 50%;
        display: inline-block;
        margin-right: 6px;
        animation: pulse 1.4s infinite;
    }
    @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.3; } 100% { opacity: 1; } }
    a { text-decoration: none !important; color: inherit !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

FALLBACK_IMG = "https://images.unsplash.com/photo-1504384308090-c894fdcc538d?w=500&q=60"
CATEGORY_FALLBACK_IMG = {
    "AI": "https://images.unsplash.com/photo-1677442136019-21780ecad995?w=500&q=60",
    "Software": "https://images.unsplash.com/photo-1517694712202-14dd9538aa97?w=500&q=60",
    "Kesehatan": "https://images.unsplash.com/photo-1505751172876-fa1923c5c528?w=500&q=60",
    "Finance": "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=500&q=60",
}


def extract_image(entry, category):
    """Coba ambil thumbnail dari berbagai kemungkinan field RSS, fallback ke gambar kategori."""
    try:
        if "media_thumbnail" in entry and entry.media_thumbnail:
            return entry.media_thumbnail[0].get("url")
        if "media_content" in entry and entry.media_content:
            return entry.media_content[0].get("url")
        for link in entry.get("links", []):
            if link.get("type", "").startswith("image"):
                return link.get("href")
        summary = entry.get("summary", "") or entry.get("description", "")
        match = re.search(r'<img[^>]+src="([^"]+)"', summary)
        if match:
            return match.group(1)
    except Exception:
        pass
    return CATEGORY_FALLBACK_IMG.get(category, FALLBACK_IMG)


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
                    "image": extract_image(entry, category),
                }
            )
        return articles
    except Exception as e:
        return [{"error": str(e), "source": source_name, "category": category}]


@st.cache_data(ttl=REFRESH_SECONDS, show_spinner=False)
def fetch_all():
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


def render_card(art):
    color = CATEGORY_COLORS.get(art["category"], "#E30513")
    st.markdown(
        f"""
        <a href="{art['link']}" target="_blank">
        <div class="news-card">
            <div class="news-img" style="background-image:url('{art['image']}')"></div>
            <div class="news-body">
                <span class="news-tag" style="background-color:{color}">{art['category'].upper()}</span>
                <div class="news-title">{art['title']}</div>
                <div class="news-meta">📰 {art['source']} &nbsp;·&nbsp; 🕒 {art['published'] or 'baru saja'}</div>
            </div>
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
st.sidebar.markdown("🔴 **LIVE** — update tiap 60 detik")

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
    '<div class="topbar"><span class="live-dot"></span>LIVE UPDATE &nbsp;|&nbsp; AI · SOFTWARE · KESEHATAN · FINANCE &nbsp;|&nbsp; '
    + datetime.now().strftime("%A, %d %B %Y — %H:%M") + '</div>',
    unsafe_allow_html=True,
)
st.markdown('<div class="brand-title">🛰️ TECH RADAR</div>', unsafe_allow_html=True)
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
            <div class="hero-card" style="background-image:url('{headline['image']}')">
                <div class="hero-overlay">
                    <span class="hero-tag" style="background-color:{color}">🔥 HEADLINE · {headline['category'].upper()}</span>
                    <div class="hero-headline">{headline['title']}</div>
                    <div class="hero-meta">📰 {headline['source']} &nbsp;·&nbsp; 🕒 {headline['published'] or 'baru saja'}</div>
                </div>
            </div>
            </a>
            """,
            unsafe_allow_html=True,
        )

    st.markdown('<div class="section-heading">📌 Berita Terbaru</div>', unsafe_allow_html=True)
    grid_cols = st.columns(2)
    for i, art in enumerate(sorted_articles[1:9]):
        with grid_cols[i % 2]:
            render_card(art)

with col_side:
    st.markdown('<div class="trending-panel">', unsafe_allow_html=True)
    st.markdown('<div class="trending-heading">🔥 Trending Dunia</div>', unsafe_allow_html=True)
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
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# HASIL PENCARIAN NEWSAPI (kalau aktif)
# ---------------------------------------------------------------------------
if use_newsapi and newsapi_key:
    st.divider()
    st.markdown(f'<div class="section-heading">🔎 Hasil Pencarian: "{custom_query}"</div>', unsafe_allow_html=True)
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
                    img = a.get("urlToImage") or FALLBACK_IMG
                    st.markdown(
                        f"""<div class="news-card">
                        <div class="news-img" style="background-image:url('{img}')"></div>
                        <div class="news-body">
                        <span class="news-tag" style="background-color:#555">NEWSAPI</span>
                        <div class="news-title">{a.get('title','')}</div>
                        <div class="news-meta">📰 {a.get('source',{}).get('name','')}</div>
                        </div></div>""",
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
    "Gambar diambil dari thumbnail artikel asli; kalau tidak tersedia, dipakai gambar kategori bawaan."
)
