# AliağaAI - Aktif Bağlam

## 📍 Şu An Neredeyiz?

### Durum: Backend & Veri Altyapısı Hazır ✅
- [x] Backend mimarisi (FastAPI) kuruldu
- [x] Veritabanı şeması (25 tablo) tamamlandı
- [x] Scraper'lar (Static & Dynamic) yazıldı
- [x] 224+ kayıt veritabanına çekildi
- [x] Otomatik güncelleyici (APScheduler) kuruldu
- [x] Docker yapılandırması tamamlandı
- [ ] AI entegrasyonu (Groq) sırada

## 🎯 Şu Anki Odak

### AI Entegrasyonu (Groq)
Veri toplama aşaması bitti. Şimdi bu verileri anlamlandıracak AI katmanına geçiyoruz.
**Hedef:** Kullanıcı sorularını doğal dilde cevaplamak.

## 🔜 Sonraki Adımlar

1. **AI Service Entegrasyonu**
   - Groq API kurulumu (lama3-8b-8192)
   - RAG yapısı (Basit search + LLM)
   
2. **Frontend MVP**
   - Next.js projesi oluştur
   - Basit arama arayüzü
   - Sonuç gösterimi

3. **Deployment**
   - Docker container'ı test et
   - Render/Railway deploy

## 📝 Son Kararlar

| Karar | Sonuç | Tarih |
|-------|-------|-------|
| Veri Toplama | Otomatik Scraping (Dynamic + Static) | 17/01/2026 |
| Güncelleme | APScheduler (Günde 2 kez) | 17/01/2026 |
| Deployment | Docker (Container) | 17/01/2026 |
| API Bütçesi | Groq (Ücretsiz Tier) | 16/01/2026 |

## ⚠️ Dikkat Edilecekler

1. **Docker Desktop:** Build için çalışıyor olması lazım.
2. **Groq Rate Limits:** Dakikalık istek sınırını aşmamak gerek.
3. **Site Değişiklikleri:** Scraper selector'ları (özellikle news) kırılabilir.
