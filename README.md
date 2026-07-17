# Tech Radar — Portal Berita Teknologi Real-Time

Dashboard Streamlit bergaya portal berita (headline, trending, grid kategori)
yang menampilkan berita terbaru untuk 4 kategori: AI, Software, Kesehatan, dan
Finance. Data diambil dari RSS feed sumber resmi (gratis, tanpa perlu API key),
plus opsi tambahan pakai NewsAPI.org kalau mau cari kata kunci spesifik.
Halaman auto-refresh tiap 60 detik.

## Cara Menjalankan

1. Install dependency:
   ```
   pip install -r requirements.txt
   ```

2. Jalankan aplikasi:
   ```
   streamlit run app.py
   ```

3. Browser otomatis terbuka di `http://localhost:8501`

## Fitur

- Layout ala portal berita: headline utama, panel "Trending Dunia", grid berita per kategori
- 4 kategori: AI, Software, Kesehatan, Finance — masing-masing narik dari 3 sumber RSS sekaligus
- Auto-refresh otomatis tiap 60 detik (pakai streamlit-autorefresh), tidak perlu reload manual
- Cache data juga 60 detik, jadi data yang tampil selalu "segar"
- Tombol "Refresh manual" di sidebar untuk paksa ambil data terbaru kapan saja
- Opsional: masukkan API key dari newsapi.org (gratis, daftar di https://newsapi.org)
  untuk pencarian kata kunci custom di luar 4 kategori bawaan

## Kalau Mau Custom

- Tambah/ganti sumber berita: edit dictionary `RSS_FEEDS` di `app.py`,
  format `"Nama Sumber": "URL_RSS"`
- Ganti interval refresh: ubah nilai `REFRESH_SECONDS` di bagian atas `app.py`
- Tambah kategori baru: tambah key baru di `RSS_FEEDS` dan `CATEGORY_ICONS`

## Catatan Penting

- Sumber RSS kadang berubah struktur URL atau server down sementara. Kalau satu
  sumber gagal, sumber lain di kategori yang sama tetap tampil (tidak bikin app crash).
- NewsAPI.org versi gratis punya limit 100 request/hari dan cuma bisa akses artikel
  30 hari terakhir — cukup untuk pemakaian pribadi harian.
- Aplikasi ini jalan lokal di komputer kamu. Kalau mau diakses dari HP/di mana saja,
  bisa di-deploy gratis ke Streamlit Community Cloud (share.streamlit.io).
