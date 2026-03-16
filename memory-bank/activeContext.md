# AliağaAI - Aktif Bağlam

## Şu Anki Durum: Frontend Navigasyon Tamamlandı — Entegrasyon Aşaması
Backend (FastAPI + PostgreSQL/pgvector) ve Frontend (React Native/Expo) altyapıları profesyonel düzeyde kuruldu. Sistem tüm katmanlarıyla (Query Router, RAG, Embedding, LLM) çalışmaya hazır.

## Son Yapılan Değişiklikler
- **Backend tamamen yeniden yapılandırıldı:**
  - Async SQLAlchemy + asyncpg + pgvector entegrasyonu.
  - Services katmanı: embedding, LLM (Groq), RAG, Query Router.
  - Yeni route'lar: `/api/chat` (AI endpoint), CRUD admin, scraping trigger'ları.
  - Docker Compose: pgvector/pgvector:pg16 + FastAPI.
- **Frontend tamamen oluşturuldu:**
  - 4 ana ekran: Asistan (chat), Keşfet (mekanlar), Eczane, Gündem (haberler+etkinlikler).
  - 3 bileşen: SearchBar, PlaceCard, ChatBubble.
  - Tema sistemi, API client (axios), tip tanımları.
  - Bottom tab navigasyon (React Navigation v7) — Ionicons ikonları.
  - Root App.tsx: NavigationContainer + SafeAreaProvider.

## Mimari Kararlar (Kesinleşmiş)
- **Embedding modeli:** `intfloat/multilingual-e5-small` (384 boyut) — Türkçe dil desteği + küçük boyut.
- **LLM:** Groq API / `llama-3.3-70b-versatile` — ücretsiz katman, hızlı çıkarım.
- **DB bağlantı:** `postgresql+asyncpg://` formatı.
- **Mobil API URL:** `http://10.0.2.2:8000/api` (dev/emulator), `https://api.aliagai.com/api` (prod).
- **Query Router akışı:** Kullanıcı sorgusu → LLM intent sınıflandırma → SQL/RAG/Hybrid veri çekme → LLM yanıt formatlama.
- **AI Prensibi:** AI karar verici değil, sadece açıklayıcı katman. Veri her zaman veritabanından gelir.

## Sıradaki Adımlar
1. **Derleme Doğrulaması:** `expo start` ile frontend'in hatasız derlenmesini doğrula.
2. **Docker Ayağa Kaldırma:** `docker-compose up --build` ile PostgreSQL + backend çalıştır.
3. **Uçtan Uca Test:** Mobil uygulamadan soru gönder → backend'de Query Router → DB sorgusu → LLM yanıt → mobil ekranda göster.
4. **Veri Doldurma:** Eczane, mekan, haber verilerini DB'ye ekle (scraper veya seed script).
5. **Scraper Adaptasyonu:** `scheduler.py` içindeki eski senkron scraper'ları async DB ile uyumlu hale getir.

## Dikkat Edilecekler
- Query Router'ın SQL/RAG ayrımı sistemin en kritik noktası — doğru intent classification şart.
- AI asla kendi başına bilgi üretmemeli — sadece DB'den gelen veriyi doğal dile çevirmeli.
- Backend Python paketleri (pgvector, sentence-transformers) Docker içinde kurulu — lokal venv'de çalışmaz.
