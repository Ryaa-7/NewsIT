# Tech Radar — Dashboard Teknologi Real-Time

Dashboard Streamlit yang menampilkan berita terbaru untuk 4 kategori:
AI, Software, Kesehatan, dan Finance. Data diambil dari RSS feed sumber
resmi (gratis, tanpa perlu API key), plus opsi tambahan pakai NewsAPI.org
kalau mau cari kata kunci spesifik.

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

- 4 tab kategori: AI, Software, Kesehatan, Finance
- Setiap kategori narik dari 3 sumber RSS berbeda sekaligus
- Cache 15 menit supaya tidak membebani server sumber, tapi tetap "hampir real-time"
- Tombol "Refresh sekarang" di sidebar untuk paksa ambil data terbaru
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
