# AliağaAI - İlerleme Takibi

## ✅ Tamamlanan

### Faz 0: Planlama (16/01/2026)
- [x] Proje fikri ve vizyon belirlendi
- [x] Veri envanteri çıkarıldı
- [x] Teknik stack kararları alındı

### Faz 1-2: Backend & Database (17/01/2026)
- [x] FastAPI proje yapısı kuruldu
- [x] PostgreSQL & SQLAlchemy kurulumu
- [x] Veritabanı şeması (25 tablo) oluşturuldu
- [x] Admin API endpointleri yazıldı

### Faz 4: Scrapers & Otomasyon (17/01/2026)
- [x] `ComprehensiveScraper` (Statik veriler)
- [x] `DynamicScraper` (Haber, Duyuru, Proje)
- [x] APScheduler kurulumu (5 cron job)
- [x] Docker yapılandırması (Dockerfile, Compose)
- [x] Veri çekimi tamamlandı (224+ kayıt)

## 🔄 Devam Eden

### Faz 3: AI Entegrasyonu
- [ ] Groq API client
- [ ] RAG yapısı (Arama + Özetleme)
- [ ] Prompt engineering

## 📋 Yapılacaklar

### Faz 5: Frontend
- [ ] Next.js kurulumu
- [ ] Arama arayüzü
- [ ] Sonuç gösterimi
- [ ] Mobil responsive tasarım

### Faz 6: Deploy
- [ ] Docker build & test
- [ ] Cloud deploy (Render/Railway)

## 🐛 Bilinen Sorunlar

- `hotels` verisi çekilemiyor (JS rendering gerekli, tarayıcı tabanlı çözüm lazım).
- `tourism_spots` ve `places` (mekanlar) için manuel giriş veya Google Maps gerekiyor.

## 📈 Metrikler

| Metrik | Hedef | Güncel |
|--------|-------|--------|
| Statik Veri | 100+ | 132 |
| Dinamik Veri | Güncel | 92 |
| Toplam Tablo | 20+ | 25 |
| Otomasyon | Günlük | ✅ (APScheduler) |

## 📝 Notlar

- Scraper'lar verimli çalışıyor, sadece `hotels` hariç.
- Docker yapısı prod için hazır.
- Scheduler `main.py` lifespan içinde otomatik başlıyor.
