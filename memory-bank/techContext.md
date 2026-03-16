# AliağaAI - Teknik Bağlam

## 🛠️ Teknoloji Stack

### Backend
- **Framework:** FastAPI (Python)
- **Database:** PostgreSQL
- **ORM:** SQLAlchemy / Prisma
- **AI:** OpenAI API veya Groq (ücretsiz)

### Frontend
- **Framework:** Next.js veya Vite + React
- **Styling:** Tailwind CSS
- **UI:** Shadcn/ui

### Scraping
- **Kütüphane:** BeautifulSoup + Requests
- **Otomasyon:** Playwright (gerekirse)
- **Zamanlama:** Cron job (nöbetçi eczane için)

## 📊 Veri Kaynakları

### Belediye Sitesi (Scraping)
| Veri | URL | Güncelleme |
|------|-----|------------|
| Nöbetçi Eczane | `/kent-rehberi/nobetci-eczane` | Günlük |
| Acil Telefonlar | `/kent-rehberi/acil-telefonlar` | Statik |
| Kamu Kuruluşları | `/kent-rehberi/kamu-kuruluslari` | Statik |
| Sağlık Kuruluşları | `/kent-rehberi/saglik-kuruluslari` | Statik |
| Oteller | `/kent-rehberi/oteller` | Statik |
| Turistik Yerler | `/aliaga/aliagada-turizm` | Statik |
| Tarihçe | `/aliaga/tarihce` | Statik |
| Gastronomi | `/aliaga/gastronomi` | Statik |

### Manuel Giriş (Google Maps)
| Kategori | Hedef Sayı |
|----------|-----------|
| Kafeler | 10-15 |
| Restoranlar | 10-15 |
| Marketler | 5 |
| Berberler | 5 |
| Diğer | 10 |

## 🗄️ Veritabanı Şeması (v4 Güncel)

### Dinamik Tablolar (Sürekli Güncel)
- `news` (Haberler - başlık, özet, resim, tarih)
- `announcements` (Duyurular - ihale, ilan, duyuru)
- `projects` (Projeler - tamamlanan, devam eden)
- `events` (Etkinlikler - tarih, yer, saat)
- `pharmacy_duties` (Nöbetçi Eczaneler)

### Statik Tablolar (Şehir Verisi)
- `public_institutions`, `schools`, `libraries`, `health_facilities`
- `services` (belediye hizmetleri)
- `neighborhoods` (muhtarlıklar)
- `history`, `geography`, `economy`
- `antique_cities`, `gastronomy`, `hiking_routes`
- `emergency_phones`

## 🔧 Geliştirme Ortamı

```
AliağAİ/
├── backend/
│   ├── app/
│   │   ├── scrapers/ (comprehensive.py, dynamic.py)
│   │   ├── models/ (SQLAlchemy tabloları)
│   │   ├── routes/ (admin.py, search.py)
│   │   ├── main.py
│   │   └── scheduler.py (APScheduler)
│   ├── Dockerfile
│   └── requirements.txt
├── docker-compose.yml
├── .env
```

## 📊 Veri Kaynakları (Güncel Durum)

| Kaynak | Durum | Kayıt Sayısı | Güncelleme |
|--------|-------|--------------|------------|
| Nöbetçi Eczane | ✅ | 2 | Günlük |
| Haberler | ✅ | 20+ | Günlük |
| Duyurular | ✅ | 20+ | Günlük |
| Projeler | ✅ | 52 | Haftalık |
| Kamu Kurumları | ✅ | 60+ | Statik |
| Mahalleler | ✅ | 36 | Statik |
| Oteller | ⚠️ | 0 | Manuel Gerekli |


## ⚠️ Kısıtlamalar

1. **API Bütçesi Yok**
   - Google Places API kullanılmayacak
   - OpenAI yerine Groq (ücretsiz) tercih edilebilir

2. **Uzaktan Çalışma**
   - Aliağa'da değilsin
   - Mekanları kendin gezemezssin
   - Manuel veri girişi Google Maps'ten

3. **MVP Odaklı**
   - Tag sistemi şimdilik yok
   - Kullanıcı geri bildirimi sonra
