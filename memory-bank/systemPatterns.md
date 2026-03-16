# AliağaAI - Sistem Mimarisi

## 🏗️ Genel Mimari

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Frontend  │────▶│   Backend   │────▶│  Database   │
│  (Next.js)  │◀────│  (FastAPI)  │◀────│ (PostgreSQL)│
└─────────────┘     └──────┬──────┘     └─────────────┘
                           │
                    ┌──────▼──────┐
                    │   AI API    │
                    │ (Groq/GPT)  │
                    └─────────────┘
```

## 🔍 Arama Akışı

```
Kullanıcı Sorusu: "aliağada sessiz kafe var mı"
         │
         ▼
┌─────────────────────────────────────────────────────┐
│ 1. KEYWORD EXTRACTION                               │
│    Input: "aliağada sessiz kafe var mı"             │
│    Output: ["sessiz", "kafe"]                       │
└─────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────┐
│ 2. CATEGORY MATCHING                                │
│    "kafe" → category: "kafe"                        │
│    "sessiz" → tag: "sessiz" (V2'de)                 │
└─────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────┐
│ 3. DATABASE QUERY                                   │
│    SELECT * FROM places                             │
│    WHERE category = 'kafe'                          │
│    ORDER BY rating DESC                             │
│    LIMIT 3                                          │
└─────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────┐
│ 4. AI SUMMARY                                       │
│    Input: 3 mekan verisi                            │
│    Output: "Aliağa'da en yüksek puanlı kafe X..."   │
└─────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────┐
│ 5. RESPONSE                                         │
│    - AI özet metni                                  │
│    - 3 mekan kartı (isim, puan, link)               │
└─────────────────────────────────────────────────────┘
```

## 📦 Bileşenler

### 1. Scheduler Service (APScheduler)
Düzenli veri güncellemelerini yönetir.
```python
# app/scheduler.py
def init_scheduler():
    # Günlük: Nöbetçi Eczane (00:05)
    # Günlük: Haberler (08:00, 18:00)
    # Haftalık: Projeler (Pzt 06:00)
    # Aylık: Statik Veriler (Ayın 1'i)
```

### 2. Scraper Service
```python
# app/scrapers/ dynamic.py & comprehensive.py
class DynamicScraper:
    def scrape_news() -> int
    def scrape_announcements() -> int
    def scrape_projects() -> int

class ComprehensiveScraper:
    def scrape_all_static() -> int
    def scrape_pharmacy() -> int
```

### 3. AI Service (Planlanan)
```python
class AIService:
    def summarize(data: List[Dict], query: str) -> str:
        # Groq API entegrasyonu
        # RAG Mimarisi
```

## 🔄 Veri Akışları

### Scraping (Otomatik)
```
APScheduler (Background)
    │
    ├── Her gün 00:05 ──▶ Eczane Scraper ──▶ DB (Yeni nöbetçi)
    │
    ├── Her gün 08:00 ──▶ Haber Scraper ──▶ DB (Yeni haberler)
    │
    └── Her ayın 1'i ───▶ Statik Scraper ──▶ DB (Tam güncelleme)
```

### Admin Tetikleme
```
POST /api/admin/scrape/news
    │
    ▼
FastAPI Route ──▶ Scraper Service ──▶ Database
    │
    ▼
Response: "20 news scraped"
```

## 🐳 Docker Mimarisi

```yaml
services:
  backend:
    image: aliagai-backend
    ports: 8000:8000
    env: .env
    restart: unless-stopped
    healthcheck: /health
```

## 🎨 Frontend Yapısı

```
src/
├── components/
│   ├── SearchInput.tsx    # Ana arama kutusu
│   ├── PlaceCard.tsx      # Mekan kartı
│   ├── AISummary.tsx      # AI özet balonu
│   └── Layout.tsx
├── pages/
│   ├── index.tsx          # Ana sayfa
│   └── api/
│       └── search.ts      # API route
└── styles/
    └── globals.css
```

## 🔐 Güvenlik

1. **Rate Limiting:** 60 istek/dakika
2. **Input Sanitization:** SQL injection koruması
3. **CORS:** Sadece frontend domain
4. **API Key:** AI servisi için .env'de
