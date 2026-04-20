# AliağaAI: Hibrit Arama Tabanlı Akıllı Şehir Rehberi

AliağaAI, Aliağa ilçesi için geliştirilmiş, yüksek performanslı bir "Hibrit Şehir Asistanı" projesidir. Sistem; yapılandırılmış SQL verilerini, modern LLM (Large Language Model) tabanlı RAG (Retrieval-Augmented Generation) mimarisiyle birleştirerek kullanıcılara doğrulanmış, bağlam uyumlu ve halüsinasyondan arındırılmış yerel bilgiler sunar.

## 1. Mimari Prensipler ve Tasarım Kararları

Projenin geliştirilmesinde aşağıdaki mühendislik prensipleri esas alınmıştır:

- **Doğruluk Önceliği:** Yapay zeka veri üretmez; sistemin bulduğu doğrulanmış veriyi doğal dilde özetler.
- **Hibrit Arama (Hybrid Search):** Sorunun doğasına göre SQL filtreleme veya Vektör benzerlik araması dinamik olarak seçilir.
- **Hız ve Ölçeklenebilirlik:** Groq altyapısı ve PostgreSQL + pgvector kullanımıyla düşük gecikme süreli yanıtlar hedeflenir.
- **Yerellik Odaklılık:** Tüm veri kaynakları sadece Aliağa ve yakın çevresine indirgenmiştir.

## 2. Detaylı Veri Katmanı ve Stratejiler

Sistemdeki veriler, erişim yöntemine ve yapısına göre üç ana kategoride yönetilmektedir.

### 2.1. SQL Katmanı (Yapılandırılmış / Filtrelenebilir)
Bu veriler kesin alanlara sahiptir ve semantik arama yerine doğrudan filtreleme gerektirir.

| Veri Tipi | Tablo Adı | Örnek Sorular | Güncelleme Periyodu |
| :--- | :--- | :--- | :--- |
| Nöbetçi Eczaneler | `pharmacies` | "Nöbetçi eczane hangisi?" | Günlük |
| Hava Durumu | `weather_cache` | "Bugün hava nasıl?" | Saatlik |
| Namaz Vakitleri | `prayer_times_cache` | "İftar saati ne zaman?" | Günlük |
| Akaryakıt Fiyatları | `fuel_prices_cache` | "Benzin kaç lira?" | Günlük |
| Döviz Kurları | `currency_cache` | "Dolar kaç TL?" | Saatlik |
| Son Depremler | `earthquakes_cache` | "Son deprem nerede oldu?" | Saatlik |
| İZBAN Seferleri | `izban_schedules` | "İZBAN saat kaçta?" | Haftalık |
| Semt Pazarları | `street_markets` | "Bugün pazar nerede?" | Sabit |
| Acil Telefonlar | `emergency_contacts` | "Ambulans numarası?" | Sabit |

### 2.2. SQL + pgvector Katmanı (Hibrit Arama)
Hem filtreleme (tarih, kategori) hem de metin bazlı anlam araması gerektiren verilerdir.

| Veri Tipi | SQL Tablosu | Vektör İçerik | Kaynak |
| :--- | :--- | :--- | :--- |
| Mekanlar | `places` | Açıklama metni | Admin Panel |
| Haberler | `news` | İçerik chunk'ları | aliaga.bel.tr |
| Etkinlikler | `events` | Açıklama metni | aliaga.bel.tr |
| Duyurular | `announcements` | İçerik metni | aliaga.bel.tr |
| Su/Elek. Kesintileri | `utility_outages` | Kesinti detayları | İZSU / GDZ |
| Belediye Projeleri | `projects` | Proje detayları | aliaga.bel.tr |

### 2.3. Sadece pgvector (Yapılandırılmamış Metin)
Filtrelenecek alanı olmayan, sadece semantik benzerlik ile erişilen ham metinlerdir.

- **Şehir Bilgisi:** Tarihçe, Antik Kentler, Turizm, Gastronomi ve Coğrafya gibi statik sayfaların chunk edilmiş halleri.

## 3. Query Router ve Niyet (Intent) Matrisi

Sisteme gelen her sorgu, LLM tarafından aşağıdaki niyetlerden birine atanır ve ilgili arama motoruna yönlendirilir.

| ID | Intent | Arama Metodu | Örnek Sorgu |
| :--- | :--- | :--- | :--- |
| 1 | `pharmacy` | SQL Only | "Açık eczane var mı?" |
| 2 | `weather` | SQL (Cache) | "Hava yağmurlu mu?" |
| 3 | `transport` | SQL | "İZBAN son sefer ne zaman?" |
| 4 | `place` | Hybrid (SQL+RAG) | "Sakin bir kafe önerir misin?" |
| 5 | `news` | Hybrid | "Otoparkla ilgili son haberler?" |
| 6 | `outage` | SQL + RAG | "Elektrik ne zaman gelecek?" |
| 7 | `event` | SQL + RAG | "Bu hafta sonu konser var mı?" |
| 8 | `emergency` | SQL | "Polis imdat numarası?" |
| 9 | `market` | SQL | "Çarşamba pazarı nerede?" |
| 10 | `city_info` | RAG Only | "Aliağa'nın tarihçesi nedir?" |
| 11 | `institution` | SQL | "Belediye binası nerede?" |
| 12 | `service` | SQL | "Acil çilingir lazım." |

*Toplam 25+ farklı niyet türü desteklenmektedir.*

## 4. Teknik Kurumsal Mimarinin Detayları

### 4.1. Backend Servis Katmanı (FastAPI)
Backend, yüksek performanslı ve asenkron (TIA) bir yapıya sahiptir.
- **API Documentation:** `/docs` (Swagger) ve `/redoc` üzerinden otomatik dökümante edilir.
- **Pydantic Schemas:** Tüm veri giriş-çıkışları tip güvenli şemalarla validate edilir.
- **CORS Management:** Güvenli frontend erişimi için konfigüre edilmiştir.

### 4.2. Veritabanı ve Vektör Veritabanı (PostgreSQL)
PostgreSQL üzerine kurulu `pgvector` eklentisi sayesinde:
- İlişkisel veriler (ACID uyumlu).
- Embedding verileri (Vektör benzerlik araması).
Tek bir instance üzerinde yönetilerek operasyonel maliyet düşürülmektedir.

### 4.3. LLM ve AI İşleme (Groq)
- **Model:** Llama-3-70b-versatile (Düşük gecikme, yüksek kapasiteli bağlam).
- **Embedding:** Metinleri vektörize etmek için `multilingual-e5-small` modeli kullanılır.

## 5. Geliştirici Rehberi ve Ortam Yapılandırması

### 5.1. Çevresel Değişkenler (.env)
Aşağıdaki değişkenler sistemin çalışması için zorunludur:

```env
# Backend
DATABASE_URL=postgresql+asyncpg://aliagai:aliagai_secret@postgres:5432/aliagai_db
GROQ_API_KEY=your_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile
EMBEDDING_MODEL=intfloat/multilingual-e5-small

# API Keys
COLLECTAPI_KEY=your_collect_api_key

# Infrastructure
POSTGRES_USER=aliagai
POSTGRES_PASSWORD=aliagai_secret
POSTGRES_DB=aliagai_db
```

### 5.2. Konteyner Yönetimi
Sistemi tam otomatik olarak başlatmak için Docker Compose kullanılır:

```bash
cd frontend
npm install
npx expo start
```

## Veri Kaynakları ve Güncelleme Stratejisi

- **CollectAPI:** Eczane, hava durumu ve ekonomi verileri için periyodik güncelleme.
- **Scraping (httpx + BeautifulSoup):** Belediye duyuruları, haberler ve kesinti bilgileri için asenkron veri toplama.
- **Seed Data:** Sabit kurum bilgileri, posta kodları ve acil numaralar.
- **Admin Panel:** Küratörlü mekan ve hizmet sağlayıcı verilerinin manuel yönetimi.

## Yol Haritası (Roadmap)

- [ ] Konum tabanlı anlık önerilerin entegrasyonu.
- [ ] Uygulama içi etkileşimli harita görünümü (Mapbox/Google Maps).
- [ ] Kullanıcı yorum ve puanlama sistemi.
- [ ] Komşu ilçelere (Menemen, Foça) hizmet genişlemesi.
- [ ] Sesli asistan ve dikreleme desteği.

## Lisans

Bu proje tüm hakları saklı olarak geliştirilmiştir. İzinsiz paylaşımı ve kullanımı yasaktır.
