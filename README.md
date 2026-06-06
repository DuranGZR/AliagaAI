<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" />
  <img src="https://img.shields.io/badge/React_Native-61DAFB?style=for-the-badge&logo=react&logoColor=black" />
  <img src="https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white" />
  <img src="https://img.shields.io/badge/pgvector-000000?style=for-the-badge&logo=postgresql&logoColor=white" />
  <img src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white" />
  <img src="https://img.shields.io/badge/Groq_LLM-F55036?style=for-the-badge&logo=meta&logoColor=white" />
</p>

<div align="center">
  <h1>🏙️ AliağaAI</h1>
  <h3>Yapay Zeka Destekli Şehir Rehberi ve Akıllı Şehir Asistanı (Full Stack)</h3>
  <p>
    <b>Aliağa ilçesine özel, mobil frontend (React Native) ve çok aşamalı RAG backend (FastAPI) mimarisiyle çalışan, doğrulanmış ve halüsinasyonsuz akıllı şehir asistanı.</b><br/>
    <i>Doğrulanmış Bilgi Deposu • Lüks Arayüz (Stitch Design) • Ajanlı Sorgu Yönlendirici • pgvector + Kelime Arama</i>
  </p>
  <p>
    <a href="#-1-mobil-uygulama-frontend-mimarisi">Frontend Mimarisi</a> •
    <a href="#-2-backend-api-ve-ajan-mimarisi">Backend Mimarisi</a> •
    <a href="#-3-rag-retrieval-augmented-generation-calisma-mantigi">RAG Çalışma Mantığı</a> •
    <a href="#-4-proje-klasör-yapisi">Klasör Yapısı</a> •
    <a href="#-5-kurulum-ve-calistirma">Kurulum</a> •
    <a href="#-6-api-dokumantasyonu">API Dokümantasyonu</a>
  </p>
</div>

---

## 🏗️ Genel Sistem Veri Akışı

Uygulamanın çalışması, kullanıcının mobil arayüzdeki etkileşiminden başlayıp, API, RAG, SQL ve LLM katmanlarından geçerek yeniden mobil uygulamaya yansıtılmasına kadar bütünleşik bir döngüden oluşur:

```mermaid
graph TD
    User([📱 Mobil Kullanıcı]) -->|1. REST İstekleri / Axios| API[⚙️ FastAPI Endpoints]
    
    subgraph Frontend (React Native)
        UI[🎨 Stitch Design / Black & Gold] -->|Context / GPS / Auth| User
        Shimmer[⏳ Shimmer placeholders / DataState] --> UI
    end
    
    subgraph Backend API & Agent
        API -->|2. Hata Düzeltici| Pre[🧹 Preprocessor]
        Pre -->|3. Niyet Analizi| Router{🤖 Agentic Query Router}
        Router -->|A. SQL Arama| SQL[🗄️ SQL DB]
        Router -->|B. Semantik Arama| pgvector[🧠 pgvector RAG]
        Router -->|C. Harici Veri| Cache[🌍 CollectAPI / Kandilli]
    end
    
    subgraph RAG Pipeline
        pgvector -->|Semantik Varyantlar| Expand[🔍 Query Expansion]
        Expand -->|Hibrit Arama| FTS[🔎 PostgreSQL FTS]
        FTS -->|Birleştirme| RRF[📈 Reciprocal Rank Fusion]
        RRF -->|Yeniden Sıralama| Rerank[📊 Rerank candidates]
    end
    
    Rerank -->|Doğrulanmış Bağlam Chunks| LLM[🤖 LLM Generator]
    SQL -->|Yapılandırılmış Tablo Verisi| LLM
    Cache -->|Canlı Ham Veri| LLM
    
    LLM -->|4. Atıf Kontrolü & Grounding| Filter[🛡️ Citation Sanitizer]
    Filter -->|5. Formatlı JSON| User
```

---

## 📱 1. Mobil Uygulama (Frontend) Mimarisi

Mobil uygulama, **React Native (Expo)** tabanlı olup, tamamen özelleştirilmiş şık bir koyu tema ve asenkron veri durumu yönetimiyle tasarlanmıştır.

### 🎨 A. Tasarım Sistemi: Stitch Design System
Uygulamanın görsel dili antik "Kültürel Miras" (Cultural Heritage) ve modern "Apple Sıvı Cam" (Liquid Glass) estetiğinden ilham almıştır:
*   **Renk Paleti (`theme/index.ts`):** 
    *   `background`: Saf Siyah (`#0A0A0A` / `#121214`) zemin.
    *   `primary`: Ege Altını / Bej vurgu tonu (`#C8A96E`).
    *   `surface`: Yarı şeffaf koyu kart yüzeyi (`rgba(30,30,30,0.80)`).
    *   `glassNav`: Pill tab bar şeffaflığı (`rgba(28,28,28,0.92)`).
*   **Tipografi:** Başlıklarda `Outfit` (Bold/ExtraBold), gövde metinlerinde ise yüksek okunurluğa sahip `Plus Jakarta Sans` yazı tipi ailesi.
*   **Harita Stili (`darkMapStyle`):** Google Haritalar arayüzü, Black & Gold temasıyla uyumlu olacak şekilde özel bir JSON şemasıyla karanlıklaştırılmıştır. Su havzaları koyu mavi (`#0a1628`), yollar koyu gri, etiketler ise altın sarısı (`#C8A96E`) olarak renklendirilmiştir.

---

### 🔀 B. Navigasyon ve Ekran Yapısı
Uygulama, `@react-navigation/native` ve `@react-navigation/bottom-tabs` ile yönetilen **3 ana sekme** (3-Tab Minimalist Bar) ve bunlara bağlı alt stack ekranlarından oluşur:

1.  **HomeScreen (Ana Ekran):**
    *   AI karşılama paneli.
    *   Hava durumu, İZBAN sefer özetleri ve bugünkü nöbetçi eczane widget'ları.
    *   **Akıllı Aksiyonlar (Intent Actions):** Kullanıcıyı doğrudan belirli niyetlerle sohbete yönlendiren dinamik kısayollar.
2.  **ChatScreen (RAG Sohbet):**
    *   AI ile izole sohbet alanı. Gelen mesajlardaki `[S1]`, `[S2]` gibi kaynak etiketlerini tıklanabilir butonlara dönüştürür.
    *   Hızlı sohbet başlatıcı öneri butonları (nöbetçi eczaneler, kesintiler, gezilecek yerler vb.).
3.  **ExploreScreen (Keşfet & Harita):**
    *   Belediye haberleri, etkinlikler ve gezi rotaları.
    *   **ExploreMap:** Kullanıcının mevcut konumu ile turistik mekanların konumlarını canlı haritada çizen, rota duraklarını birleştiren etkileşimli harita katmanı.
4.  **Yardımcı Ekranlar:**
    *   `DirectoryScreen`: Nöbetçi eczaneler, taksi durakları, kamu kurumları, okullar, bankalar ve acil numaraları listeleyen şehir rehberi.
    *   `MunicipalityScreen`: Belediye duyuruları, ihaleleri, aktif projeleri ve güncel iş ilanları.
    *   `IzbanScheduleScreen` / `OutageListScreen` / `EarthquakeListScreen` / `WeatherDetailScreen` / `LoginScreen` / `RegisterScreen`.

---

### 🛡️ C. Context Sağlayıcılar (Global State)
*   **AuthContext:** JWT token doğrulaması, kullanıcı kayıt/giriş durumlarının lokal depolamada (`AsyncStorage`) tutulması ve Google OAuth (`expo-auth-session`) entegrasyonu.
*   **LocationContext:** `expo-location` kütüphanesini kullanarak kullanıcının GPS konumunu okur ve konum tabanlı sıralamalar için koordinatları saklar.

---

### ⏳ D. Durum ve Hata Yönetimi
*   **Shimmer placeholders (`ShimmerPlaceholder`):** Veriler API'den çekilirken donuk yükleme simgeleri yerine kartların şeklini alan yumuşak geçişli animasyonlu paneller gösterilir.
*   **DataStatePanel:** Ağ hatalarında, veri bulunamadığında veya rate limit aşımında kullanıcıya "Yeniden Dene" butonuyla birlikte şık hata ekranları sunar.

---

## ⚙️ 2. Backend (API ve Ajan) Mimarisi

Backend, asenkron yapıda çalışan **FastAPI** web framework'ünü temel alır. 

### 🛡️ A. API Güvenliği ve Hız Sınırları (Security & Rate Limiting)
*   **verify_api_key:** Endpoint'ler `X-API-Key` header doğrulamasıyla korunur. `.env` dosyasındaki anahtarla eşleşmeyen istekler `403 Forbidden` ile reddedilir.
*   **SlowAPI:** `/api/v1/chat` uç noktası, sunucuyu DDoS saldırılarından ve API kota aşımından korumak için IP tabanlı istek sınırlayıcıya (Rate Limiter) sahiptir.

### 🔄 B. Arka Plan Görevleri (APScheduler)
FastAPI, `main.py:lifespan` döngüsünde arka planda bir zamanlayıcı (`apscheduler.schedulers.asyncio.AsyncIOScheduler`) ayağa kaldırır. Bu zamanlayıcı, verilerin güncel kalması için 9 farklı asenkron botu (scrapers) yönetir. Herhangi bir botta oluşabilecek hata (örn. belediye sitesinin çökmesi), diğer botları ve API'yi etkilemeyecek şekilde izole edilmiştir.

---

## 🧠 3. RAG (Retrieval-Augmented Generation) Çalışma Mantığı

AliağaAI'ın en kritik bölümü, semantik aramaları sıfır uydurma veri (grounding) ile yöneten RAG motorudur.

```
[Kullanıcı Sorgusu] ──► [Sorgu Düzeltme] ──► [LLM Sorgu Genişletme (4 Varyant)]
                                                       │
         ┌─────────────────────────────────────────────┴─────────────────────────────────────────────┐
         ▼ (Passage: e5 Embeddings)                                                                  ▼ (FTS Turkish Plain Query)
┌──────────────────────────────────────────┐                                                ┌──────────────────────────────────────────┐
│             Vektörel Arama               │                                                │              Lexical Arama               │
│ - pgvector HNSW kosinüs benzerliği       │                                                │ - PostgreSQL Full-Text Search            │
│ - Dinamik Eşik: 0.35 (Kısa sorguda 0.28) │                                                │ - plainto_tsquery('turkish')             │
└────────────────────┬─────────────────────┘                                                └────────────────────┬─────────────────────┘
                     │                                                                                           │
                     └─────────────────────────────────────┬─────────────────────────────────────────────────────┘
                                                           ▼
                                            ┌─────────────────────────────┐
                                            │ Reciprocal Rank Fusion (RRF)│
                                            │   (%70 Vektör + %30 Lexical)│
                                            └──────────────┬──────────────┘
                                                           ▼
                                            ┌─────────────────────────────┐
                                            │      Lexical Rescue         │
                                            │ (FTS Skoru >= 0.4 ise ekle) │
                                            └──────────────┬──────────────┘
                                                           ▼
                                            ┌─────────────────────────────┐
                                            │       Reranker Filtre       │
                                            │  (Kelime çakışması analizi) │
                                            └──────────────┬──────────────┘
                                                           ▼
                                            ┌─────────────────────────────┐
                                            │        Groq LLM Context     │
                                            └─────────────────────────────┘
```

### 📋 RAG İş Akışı Adımları:

1.  **Veri İndeksleme (Ingestion):**
    *   Haber, etkinlik ve belediye projelerinin uzun metinleri, `chunking.py` tarafından anlamlı bir şekilde maksimum **900 karakter** uzunluğunda parçalara bölünür.
    *   Her bir parçanın SHA256 hash değeri hesaplanır. Yalnızca içeriği değişmiş veya yeni eklenmiş parçalar vektörize edilmek üzere indexer'a gönderilir.
    *   Lokalde koşturulan `intfloat/multilingual-e5-small` embedding modeli ile **384 boyutlu** vektörler üretilir. Model kuralı gereği, indeksleme esnasında metinlerin başına `passage: ` ön eki eklenir.
2.  **Sorgu Genişletme (Query Expansion):**
    *   Kullanıcının girdiği kelimeler (örn: "egitim") LLM yardımıyla semantik olarak genişletilir ve **4 farklı varyant** sorgu üretilir (örn: "okul", "lise", "üniversite", "Aliağa eğitim").
3.  **Çok Kanallı Arama (Multi-Stage Retrieval):**
    *   **Vektör Arama:** Genişletilmiş sorgulara `query: ` ön eki eklenerek embedding vektörleri üretilir. pgvector üzerinde **HNSW (Hierarchical Navigable Small World)** indeksi kullanılarak kosinüs benzerliği ile veritabanında semantik arama yapılır.
    *   **Kelime Tabanlı Arama (Lexical):** PostgreSQL FTS (Full-Text Search) ile kelime bazlı tam eşleşmeler taranır.
4.  **Birleştirme ve Yeniden Sıralama (Fusion & Reranking):**
    *   **Reciprocal Rank Fusion (RRF):** Vektör ve kelime aramalarından gelen adaylar sıralamalarına göre birleştirilir (Ağırlık: %70 Vektör, %30 Kelime).
    *   **Lexical Rescue:** Vektör benzerliği `0.35` alt limitine takılsa bile, kelime eşleşme skoru `0.40` ve üzeri olan dökümanlar kurtarılır.
    *   **Rerank:** Aday dökümanlar, sorgu kelimeleri ile olan doğrudan çakışma yoğunluğuna göre yeniden sıralanarak en iyi `k=5` döküman seçilir.
5.  **Ajanlı Yönlendirme (Agentic Tool Calling):**
    *   Ajan (`AgenticRAGService`), kullanıcının niyetine göre 13 farklı asenkron veritabanı aracından hangisini çağıracağına Groq Tool Calling ile karar verir.
6.  **Doğrulama ve Atıf Güvenliği (Citations & Grounding):**
    *   LLM'e sadece bağlamda yer alan verileri kullanma kuralı uygulanır. Cevapta kullanılan bilgilerin döküman numaraları `[S1]`, `[S2]` şeklinde belirtilir.
    *   API çıkışında, veritabanından çekilmeyen uydurma atıf etiketleri regex filtresiyle otomatik olarak temizlenir.

---

## 📦 Proje Klasör Yapısı

<details>
<summary>📂 <b>Backend Detaylı Klasör Ağacı</b> (Göster/Gizle)</summary>

```
backend/
├── alembic/                      # Veritabanı migrasyon dosyaları
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints/
│   │       │   ├── auth.py       # Kullanıcı giriş, kayıt ve Google login
│   │       │   ├── chat.py       # RAG Chat endpoint (/chat)
│   │       │   ├── city.py       # İZBAN, pazar, namaz, hava durumu API uçları
│   │       │   ├── pharmacies.py # Nöbetçi eczane endpoint'leri
│   │       │   └── places.py     # Mekan ve kuruluş listeleme API uçları
│   │       └── api.py            # API rotalarını birleştiren router
│   ├── core/
│   │   ├── auth.py               # API Key ve JWT token verify dependencies
│   │   ├── config.py             # Pydantic Settings (Tüm .env yapılandırması)
│   │   └── limiter.py            # SlowAPI rate limiter nesnesi
│   ├── models/
│   │   ├── cache.py              # Hava durumu, döviz, deprem cache tabloları
│   │   ├── city.py               # İZBAN, Feribot, Pazar ve pgvector DocumentChunk
│   │   ├── content.py            # Haber, etkinlik, duyuru, proje, cenaze tabloları
│   │   └── places.py             # Eczane, mekan, kamu kurumları tabloları
│   ├── schemas/                  # Pydantic validation şemaları
│   ├── services/
│   │   ├── agent/                # Ajan tanımları (definitions, tools, prompt)
│   │   ├── chunk_indexer.py      # pgvector döküman senkronizasyon servisi
│   │   ├── chunking.py           # Anlamsal metin parçalayıcı
│   │   ├── collectapi_client.py  # CollectAPI asenkron veri çekim botu
│   │   ├── embedding.py          # sentence-transformers embedding servisi
│   │   ├── llm.py                # Groq / OpenAI asenkron API wrapper
│   │   ├── rag.py                # Çok aşamalı RAG (RRF, Rerank, Rescue)
│   │   └── scheduler.py          # APScheduler görev zamanlayıcı servisi
│   ├── database.py               # AsyncEngine ve get_db asenkron oturum yönetimi
│   └── main.py                   # FastAPI uygulaması başlangıç noktası
├── requirements.txt              # Backend kütüphane bağımlılıkları
└── Dockerfile                    # Backend Docker derleme talimatları
```
</details>

<details>
<summary>📂 <b>Frontend Detaylı Klasör Ağacı</b> (Göster/Gizle)</summary>

```
frontend/
├── src/
│   ├── components/
│   │   ├── AppHeader.tsx         # Ortak uygulama başlığı (≡ ALİAĞAİ 🔔)
│   │   ├── ChatBubble.tsx        # Tıklanabilir RAG citation butonları içeren bubble
│   │   ├── DataStatePanel.tsx    # Hata, boş veri ve yeniden yükleme durum paneli
│   │   ├── ExploreMap.tsx        # Harita marker çizim ve rota gösterim katmanı
│   │   └── SearchBar.tsx         # Modern, minimalist arama çubuğu
│   ├── context/
│   │   ├── AuthContext.tsx       # JWT oturumu ve Google Login Context
│   │   └── LocationContext.tsx   # GPS koordinatlarını izleyen konum Context
│   ├── navigation/
│   │   └── AppNavigator.tsx      # Yüzen Pill Tab Bar ve ekran stack navigasyonu
│   ├── screens/
│   │   ├── HomeScreen.tsx        # Ana ekran (Hava durumu, İZBAN, eczane widget'ları)
│   │   ├── ChatScreen.tsx        # RAG Sohbet arayüzü ve öneri promptları
│   │   ├── ExploreScreen.tsx     # Harita destekli mekan ve rota keşfetme ekranı
│   │   ├── DirectoryScreen.tsx   # Kategorize edilmiş taksi, kurum, hastane rehberi
│   │   └── MunicipalityScreen.tsx# Belediye haberleri, projeleri ve iş ilanları
│   ├── services/
│   │   └── api.ts                # Axios backend API istemcisi
│   ├── theme/
│   │   └── index.ts              # Renk, boşluk, yazı tipi ve harita stil şeması
│   ├── types/
│   │   └── index.ts              # TypeScript arayüz tip tanımları
│   └── utils/
│       ├── alert.ts              # Platform uyumlu özelleştirilmiş alert
│       ├── dataState.ts          # API loading ve refresh yardımcı durum yöneticisi
│       └── externalActions.ts    # Yol tarifi, arama ve tarayıcı açma aksiyonları
├── App.tsx                       # Fontların yüklendiği ana Expo bileşeni
├── package.json                  # Frontend kütüphane bağımlılıkları
└── Dockerfile                    # Frontend Docker derleme talimatları
```
</details>

---

## ⚙️ Kurulum ve Çalıştırma

### A. 🐳 Docker Compose ile Hızlı Başlangıç

Sistemde Docker kuruluysa tek bir komutla tüm uygulamayı çalıştırabilirsiniz.

1.  Kök dizindeki `.env.example` dosyasını `.env` aduyla kopyalayın:
    ```bash
    cp .env.example .env
    ```
2.  `.env` dosyasını açıp API anahtarlarınızı doldurun:
    ```ini
    GROQ_API_KEY=gsk_...
    COLLECTAPI_KEY=apikey ...
    ```
3.  Container'ları derleyip çalıştırın:
    ```bash
    docker compose up --build
    ```

---

### B. 🔧 Lokal Geliştirme Ortamı (Manuel Kurulum)

#### 1. Backend Kurulumu
1.  `backend` dizinine geçin ve sanal ortam oluşturup aktif edin:
    ```bash
    cd backend
    python -m venv venv
    venv\Scripts\activate      # Windows
    source venv/bin/activate    # macOS/Linux
    ```
2.  Bağımlılıkları yükleyin:
    ```bash
    pip install -r requirements.txt
    ```
3.  PostgreSQL veritabanınızı oluşturup `.env` içindeki `DATABASE_URL` değerini güncelleyin.
4.  Tabloları oluşturmak için Alembic göçlerini uygulayın:
    ```bash
    alembic upgrade head
    ```
5.  Başlangıç verilerini veritabanına yükleyin:
    ```bash
    python scripts/reseed_db.py
    ```
6.  FastAPI sunucusunu başlatın:
    ```bash
    uvicorn app.main:app --reload --port 8000
    ```

#### 2. Frontend Kurulumu
1.  `frontend` dizinine geçip bağımlılıkları yükleyin:
    ```bash
    cd ../frontend
    npm install
    ```
2.  Geliştirme sunucusunu başlatın:
    ```bash
    npx expo start --web
    ```

---

## 🔌 API Dokümantasyonu

### 📍 1. Sohbet Asistanı (`POST /api/v1/chat`)

<details>
<summary><b>İstek (Request Body) Örneği</b></summary>

```json
{
  "message": "Bugün Aliağa'da nöbetçi eczane hangisi?",
  "conversation_history": []
}
```
</details>

<details>
<summary><b>Yanıt (Response Body) Örneği</b></summary>

```json
{
  "answer": "Bugün Aliağa'da nöbetçi olan eczaneler şunlardır: \n• Şifa Eczanesi (İstiklal Cad. No:42, Tel: 0232 616 11 22) [S1]",
  "intent": "pharmacy",
  "search_method": "sql",
  "sources": [
    {
      "type": "pharmacy",
      "title": "Nöbetçi Eczaneler"
    }
  ],
  "response_policy": "agentic_grounded",
  "confidence": 0.85,
  "follow_up_suggestions": [
    "Eczanenin yol tarifini alabilir miyim?",
    "Yarın hangi eczaneler nöbetçi?"
  ]
}
```
</details>

### 📍 2. Nöbetçi Eczaneler (`GET /api/v1/pharmacies/duty`)
### 📍 3. İZBAN Saatleri (`GET /api/v1/city/izban`)
### 📍 4. Kesintiler (`GET /api/v1/city/outages`)

---

## 👥 Geliştirici

**Duran Gezer**  
Bu proje, İnönü Üniversitesi Mühendislik Fakültesi Bilgisayar Mühendisliği Bölümü bitirme projesi olarak tasarlanmış ve geliştirilmiştir.

---

## 📄 Lisans

Bu projenin tüm hakları saklıdır. Eğitim ve akademik değerlendirme amaçları dışında izinsiz kopyalanması, dağıtılması ve ticari kullanımı yasaktır.
