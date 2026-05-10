<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" />
  <img src="https://img.shields.io/badge/React_Native-61DAFB?style=for-the-badge&logo=react&logoColor=black" />
  <img src="https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white" />
  <img src="https://img.shields.io/badge/pgvector-000000?style=for-the-badge&logo=postgresql&logoColor=white" />
  <img src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white" />
  <img src="https://img.shields.io/badge/Groq_LLM-F55036?style=for-the-badge&logo=meta&logoColor=white" />
</p>

<h1 align="center">🏙️ AliağaAI</h1>
<h3 align="center">Hibrit RAG Mimarisi ile Çalışan Akıllı Şehir Asistanı</h3>

<p align="center">
  <i>Aliağa ilçesine özel, yapay zekâ destekli şehir rehberi ve sohbet asistanı.</i><br/>
  <i>Gerçek zamanlı veriler • Halüsinasyonsuz yanıtlar • Tamamen yerel odaklı</i>
</p>

---

## 📌 Proje Hakkında

**AliağaAI**, Aliağa ilçesi için sıfırdan tasarlanmış, üretim seviyesinde bir **Akıllı Şehir Asistanı** projesidir. Kullanıcılar mobil uygulama üzerinden doğal dilde soru sorarak nöbetçi eczanelerden hava durumuna, şehir tarihçesinden güncel haberlere, ulaşım bilgilerinden mekan önerilerine kadar geniş bir yelpazede **doğrulanmış ve kaynak gösterimli** yanıtlar alır.

Sistem, klasik bir chatbot'tan farklı olarak **Retrieval-Augmented Generation (RAG)** mimarisini temel alır. Yapay zekâ modeli kendi bilgisinden uydurma yapmak yerine, her yanıtı veritabanındaki doğrulanmış kaynaklara dayandırır.

### Temel Farklar

| Klasik Chatbot | AliağaAI |
|:---|:---|
| LLM bilgisine dayalı cevaplar | Veritabanı kaynaklarına dayalı cevaplar |
| Güncelliği belirsiz | Gerçek zamanlı veri (eczane, hava, kur) |
| Genel bilgi | Sadece Aliağa odaklı yerel bilgi |
| Halüsinasyon riski yüksek | Anti-halüsinasyon katmanı ile korumalı |
| Kaynak belirtmez | Her yanıtta kaynak referansı |

---

## 🏗️ Sistem Mimarisi

```
┌─────────────────────────────────────────────────────────────────┐
│                        KULLANICI                                │
│                   (React Native / Expo)                          │
└───────────────────────┬─────────────────────────────────────────┘
                        │ HTTP / REST
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│                     FastAPI Backend                              │
│  ┌──────────┐  ┌──────────────┐  ┌───────────────────────────┐  │
│  │ Rate     │  │ Intent       │  │ Query Router              │  │
│  │ Limiter  │→ │ Analyzer     │→ │ (SQL / RAG / Hybrid)      │  │
│  └──────────┘  └──────────────┘  └─────────┬─────────────────┘  │
│                                            │                    │
│                 ┌──────────────────────────┼──────────────┐     │
│                 ▼                          ▼              ▼     │
│  ┌──────────────────┐  ┌──────────────────────┐  ┌───────────┐ │
│  │ SQL Katmanı      │  │ pgvector (RAG)       │  │ Groq LLM  │ │
│  │ (Eczane, Hava,   │  │ (Haberler, Mekanlar, │  │ Llama-3.3 │ │
│  │  Kur, Deprem...) │  │  Tarihçe, Etkinlik)  │  │ 70B       │ │
│  └──────────────────┘  └──────────────────────┘  └───────────┘ │
│                                                                 │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────────────┐ │
│  │ Persona     │  │ Scheduler    │  │ Otonom Veri Botları     │ │
│  │ Engine      │  │ (APScheduler)│  │ (Belediye, OSM, İZSU)  │ │
│  └─────────────┘  └──────────────┘  └────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│              PostgreSQL 17 + pgvector                           │
│  Yapılandırılmış tablolar + 384-boyutlu vektör embeddingler    │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🧠 RAG Pipeline Detayları

AliağaAI'nin arama motoru üç katmanlı bir pipeline ile çalışır:

### 1. Niyet Analizi (Intent Detection)
Kullanıcının sorusu LLM tarafından analiz edilerek **25+ farklı niyet kategorisinden** birine atanır. Bu aşamada hangi veri kaynağına başvurulacağı belirlenir.

### 2. Veri Çekme (Retrieval)
Belirlenen niyete göre üç farklı arama stratejisinden biri devreye girer:

| Strateji | Kullanım Alanı | Örnek |
|:---|:---|:---|
| **SQL Only** | Yapılandırılmış, filtrelenebilir veriler | Nöbetçi eczane, hava durumu, döviz |
| **Hybrid (SQL + RAG)** | Hem filtre hem anlam araması gereken veriler | Mekanlar, haberler, etkinlikler |
| **RAG Only** | Yapılandırılmamış metin bilgisi | Şehir tarihçesi, coğrafya, turizm |

### 3. Yanıt Üretimi (Grounded Generation)
Çekilen veriler LLM'e bağlam olarak sunulur. Model **yalnızca** bu bağlamdaki bilgilere dayanarak yanıt üretir. Anti-halüsinasyon kuralları bu aşamada devreye girer:

- Bağlamda olmayan bilgi **eklenmez**
- Adres, telefon, saat gibi bilgiler **uydurulmaz**
- Kaynaklarda bilgi yoksa kullanıcıya **dürüstçe** bildirilir
- Her yanıt bir güven skoru (`confidence`) ile etiketlenir

---

## 📊 Veri Kaynakları ve Katmanlar

### Yapılandırılmış Veri (SQL)

| Veri Tipi | Tablo | Güncelleme | Kaynak |
|:---|:---|:---|:---|
| Nöbetçi Eczaneler | `pharmacies` | Günlük | CollectAPI |
| Hava Durumu | `weather_cache` | Saatlik | CollectAPI |
| Namaz Vakitleri | `prayer_times_cache` | Günlük | CollectAPI |
| Akaryakıt Fiyatları | `fuel_prices_cache` | Günlük | CollectAPI |
| Döviz Kurları | `currency_cache` | Saatlik | CollectAPI |
| Altın Fiyatları | `gold_cache` | Saatlik | CollectAPI |
| Son Depremler | `earthquakes_cache` | Saatlik | Kandilli API |
| İZBAN Seferleri | `izban_schedules` | Haftalık | İZBAN |
| Feribot Seferleri | `ferry_schedules` | Haftalık | İzdeniz |
| Semt Pazarları | `street_markets` | Sabit | Manuel |
| Acil Telefonlar | `emergency_contacts` | Sabit | Manuel |

### Hibrit Veri (SQL + pgvector)

| Veri Tipi | Tablo | Kaynak |
|:---|:---|:---|
| Mekanlar ve İşletmeler | `places` | OpenStreetMap + Manuel |
| Haberler | `news` | aliaga.bel.tr Scraper |
| Etkinlikler | `events` | aliaga.bel.tr Scraper |
| Duyurular | `announcements` | aliaga.bel.tr Scraper |
| Belediye Projeleri | `projects` | aliaga.bel.tr Scraper |
| İş İlanları | `job_listings` | aliaga.bel.tr Scraper |
| Su / Elektrik Kesintileri | `utility_outages` | İZSU / GDZ Scraper |
| Vefat İlanları | `obituaries` | İzmir Mezarlıklar Scraper |
| Kurumlar | `institutions` | Seed Data |

### Bilgi Katmanları (pgvector — Saf Metin)

| Katman | İçerik |
|:---|:---|
| `tarih` | Aliağa'nın kuruluşu, antik kentler, Kurtuluş Savaşı dönemi |
| `cografya` | İklim, bitki örtüsü, topografya |
| `ekonomi` | Sanayi bölgeleri, rafineri, liman bilgileri |
| `turizm` | Plajlar, doğa alanları, termal kaynaklar |
| `gastronomi` | Yöresel yemekler, lezzetler |
| `ulasim` | İZBAN, otoyol, feribot bağlantıları |
| `mahalleler` | İlçe mahalleleri ve nüfus bilgileri |

---

## 🤖 Otonom Veri Toplama Botları

Sistem, verilerini güncel tutmak için arka planda çalışan **otonom scraper** botlarına sahiptir:

| Bot | Kaynak | Toplanan Veri |
|:---|:---|:---|
| `scraper_aliaga_bel` | aliaga.bel.tr | Haberler, duyurular, etkinlikler, projeler, iş ilanları |
| `scraper_news` | Çeşitli kaynaklar | Aliağa ile ilgili güncel haberler |
| `scraper_outages` | İZSU / GDZ Elektrik | Su ve elektrik kesinti bildirileri |
| `scraper_osm_places` | OpenStreetMap (Overpass) | Kafe, restoran, market, ATM, otel vb. |
| `scraper_izmir_mezarlik` | İzmir Büyükşehir | Vefat ve cenaze bilgileri |
| `scraper_izmir_open_data` | İzmir Açık Veri | Belediye hizmet verileri |
| `scraper_knowledge_layers` | Vikipedi + Manuel | Tarih, coğrafya ve kültür bilgileri |
| `collectapi_client` | CollectAPI | Eczane, hava, kur, yakıt, namaz, deprem |

Tüm botlar **APScheduler** ile periyodik olarak tetiklenir ve toplanan veriler otomatik olarak vektör veritabanına indekslenir.

---

## 📱 Mobil Uygulama (Frontend)

React Native (Expo) ile geliştirilmiş, **Black & Gold** premium tasarıma sahip mobil uygulamadır.

### Ekranlar

| Ekran | Açıklama |
|:---|:---|
| **Ana Sayfa** | Hava durumu, güncel haberler, hızlı erişim kartları |
| **Keşfet** | Kategorilere göre mekan ve içerik keşfi |
| **Sohbet (AI Chat)** | Doğal dilde soru-cevap asistanı |
| **Mekan Detay** | Mekan bilgileri, adres, çalışma saatleri |
| **Haber Detay** | Haber içeriğinin tam görünümü |
| **Eczane Listesi** | Nöbetçi eczaneler ve konum bilgileri |
| **Mekan Listesi** | Kategoriye göre filtrelenmiş mekan listesi |
| **Profil / Ayarlar** | Kullanıcı tercihleri ve uygulama ayarları |

---

## ⚙️ Teknoloji Yığını

| Katman | Teknoloji | Açıklama |
|:---|:---|:---|
| **Backend** | FastAPI (Python 3.11+) | Asenkron API sunucusu |
| **Veritabanı** | PostgreSQL 17 + pgvector | İlişkisel + vektör veritabanı |
| **LLM** | Groq (Llama-3.3-70B) | Düşük gecikmeli büyük dil modeli |
| **Embedding** | multilingual-e5-small (384d) | Çok dilli metin vektörleştirme |
| **Frontend** | React Native + Expo | Çapraz platform mobil uygulama |
| **Konteynerizasyon** | Docker Compose | Tek komutla tam dağıtım |
| **Zamanlayıcı** | APScheduler | Periyodik veri güncelleme |
| **Web Scraping** | httpx + BeautifulSoup4 | Asenkron veri toplama |
| **Rate Limiting** | SlowAPI | API kötüye kullanım koruması |

---

## 🚀 Kurulum ve Çalıştırma

### Ön Gereksinimler

- [Docker](https://docs.docker.com/get-docker/) ve [Docker Compose](https://docs.docker.com/compose/install/)
- [Groq API Anahtarı](https://console.groq.com/) (ücretsiz)
- [CollectAPI Anahtarı](https://collectapi.com/) (eczane, hava durumu vb. için)

### 1. Depoyu Klonlayın

```bash
git clone https://github.com/DuranGZR/AliagaAI.git
cd AliagaAI
```

### 2. Ortam Değişkenlerini Ayarlayın

```bash
cp .env.example .env
```

`.env` dosyasını açın ve **en az** şu iki anahtarı doldurun:

```env
GROQ_API_KEY=gsk_buraya_kendi_anahtariniz
COLLECTAPI_KEY=buraya_kendi_anahtariniz
```

### 3. Docker ile Başlatın

```bash
# Tüm servisleri başlat (PostgreSQL + Backend + Frontend)
docker compose up --build
```

Sistem başlatıldığında otomatik olarak:
- ✅ PostgreSQL veritabanı ve pgvector eklentisi oluşturulur
- ✅ Tablo şemaları migrate edilir
- ✅ Başlangıç verileri (seed data) yüklenir
- ✅ Embedding modeli ısıtılır (warmup)
- ✅ Periyodik veri toplama görevleri başlatılır

### 4. Erişim Noktaları

| Servis | Adres |
|:---|:---|
| Backend API | `http://localhost:8000` |
| Swagger Docs | `http://localhost:8000/docs` |
| ReDoc | `http://localhost:8000/redoc` |
| Frontend (Web) | `http://localhost:19006` |
| PostgreSQL | `localhost:5432` |

### 5. Servisleri Ayrı Ayrı Başlatma

```bash
# Sadece veritabanı
docker compose up -d postgres

# Veritabanı + Backend
docker compose up -d postgres backend

# Sadece Frontend (backend çalışıyor olmalı)
docker compose up frontend
```

### 6. Durdurma

```bash
# Servisleri durdur
docker compose down

# Servisleri durdur ve veritabanı verisini sil
docker compose down -v
```

---

## 📁 Proje Yapısı

```
AliagaAI/
├── backend/
│   ├── app/
│   │   ├── api/v1/endpoints/     # REST API uç noktaları
│   │   ├── core/                 # Yapılandırma ve ayarlar
│   │   ├── models/               # SQLAlchemy ORM modelleri
│   │   ├── schemas/              # Pydantic veri şemaları
│   │   ├── services/
│   │   │   ├── pipeline/         # Modüler AI pipeline (Intent, Generation)
│   │   │   ├── query_router.py   # Ana sorgu yönlendirici
│   │   │   ├── rag.py            # Hibrit arama motoru
│   │   │   ├── persona.py        # Kişilik ve üslup motoru
│   │   │   ├── llm.py            # Groq LLM istemcisi
│   │   │   ├── chunk_indexer.py  # Vektör indeksleme servisi
│   │   │   ├── embedding.py      # Metin vektörleştirme
│   │   │   ├── scheduler.py      # Zamanlanmış görev yöneticisi
│   │   │   └── scraper_*.py      # Otonom veri toplama botları
│   │   ├── database.py           # Veritabanı bağlantı havuzu
│   │   └── main.py               # FastAPI uygulama giriş noktası
│   ├── scripts/                  # Yardımcı betikler (seed, sync, eval)
│   ├── evaluation/               # RAG değerlendirme test setleri
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── screens/              # Uygulama ekranları
│   │   ├── components/           # Yeniden kullanılabilir bileşenler
│   │   ├── services/             # API istemcisi
│   │   ├── navigation/           # Ekran yönlendirme
│   │   ├── theme/                # Tasarım sistemi (Black & Gold)
│   │   └── types/                # TypeScript tip tanımları
│   ├── Dockerfile
│   └── package.json
├── docker-compose.yml            # Tam orkestrasyon dosyası
├── .env.example                  # Ortam değişkenleri şablonu
└── README.md
```

---

## 🔒 Güvenlik Önlemleri

- **Rate Limiting:** Chat API uç noktası dakikada maksimum istek sayısıyla sınırlandırılmıştır
- **Anti-Halüsinasyon:** LLM, kaynakta olmayan bilgiyi kesinlikle üretmez
- **Ortam Değişkenleri:** API anahtarları `.env` dosyasında tutulur, repoya dahil edilmez
- **CORS Koruması:** Sadece yetkili origin'lerden gelen istekler kabul edilir
- **Bağlantı Havuzu:** PostgreSQL bağlantı limitleri (20+20) yapılandırılmıştır

---

## 📈 Yol Haritası

- [x] Hibrit arama motoru (SQL + pgvector RAG)
- [x] 25+ niyet kategorisi ile akıllı yönlendirme
- [x] Gerçek zamanlı veri toplama botları
- [x] Anti-halüsinasyon katmanı
- [x] Premium Black & Gold mobil tasarım
- [x] Docker Compose ile tek komutla dağıtım
- [x] Sohbet geçmişi ve bağlam belleği
- [ ] Konum tabanlı anlık öneriler
- [ ] Uygulama içi etkileşimli harita (Mapbox)
- [ ] Kullanıcı yorum ve puanlama sistemi
- [ ] Komşu ilçelere hizmet genişlemesi (Menemen, Foça)
- [ ] Sesli asistan desteği

---

## 👤 Geliştirici

**Duran Gezer**

Bu proje, İnönü Üniversitesi Bilgisayar Mühendisliği Bölümü bitirme projesi olarak geliştirilmiştir.

---

## 📄 Lisans

Bu proje tüm hakları saklı olarak geliştirilmiştir. İzinsiz kopyalanması, dağıtılması veya ticari kullanımı yasaktır.
