<div align="center">
  <h1>🌟 AliağaAI</h1>
  <p><b>Aliağa'nın Yerel Yapay Zeka Rehberi</b></p>
  <p><i>Karmaşık arama sonuçlarına ve reklam dolu sayfalara son! Aliağa'da aradığınız her şeyi saniyeler içinde bulan akıllı yapay zeka rehberiniz.</i></p>

  <p>
    <img src="https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi" alt="FastAPI" />
    <img src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="Docker" />
    <img src="https://img.shields.io/badge/Groq-000000?style=for-the-badge&logo=groq&logoColor=white" alt="Groq" />
    <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
  </p>
</div>

<hr/>

## 🎯 Proje Hakkında

**AliağaAI**, İzmir'in Aliağa ilçesine özel olarak geliştirilmiş, yerel verilerle çalışan, kullanıcı sorularını anlayıp en doğru ve güncel bilgiyi sunan bir yapay zeka rehberidir. Geleneksel arama motorlarının (Google vb.) sunduğu karmaşık ve dağınık sonuçlar yerine; net, doğrudan ve insan gibi yanıtlar üretir.

**Örnek Kullanım Senaryoları:**
- *"Şu an açık olan nöbetçi eczaneler hangileri?"*
- *"Aileyle gidilebilecek, deniz kenarı sessiz bir balık restoranı nerede?"*
- *"Aliağa'da bugün hangi etkinlikler var?"*

> **Farkımız:** Sistem halüsinasyon (uydurma) yapmaz. Kararı arka plandaki algoritma verir, yapay zeka ise sadece bu veriyi doğal bir dille kullanıcıya aktarır.

## ✨ Özellikler

- **📍 Tamamen Yerel Odak:** Sadece Aliağa'ya özel, rafine edilmiş veri seti.
- **🤖 Akıllı Yanıt Sistemi:** LLM (Groq API) entegrasyonu ile doğal dilde soruları anlama ve cevaplama.
- **⚡ Yüksek Performans:** FastAPI ile geliştirilmiş asenkron, hızlı arka uç (backend).
- **🐳 Kolay Kurulum:** Docker Compose ile tek tıkla ayağa kaldırma imkanı.
- **🗺️ Harita Entegrasyonu:** Bulunan mekanlar için anında yol tarifi alabileceğiniz harita linkleri.

## 🛠️ Teknoloji Yığını

* **Backend:** FastAPI (Python)
* **AI Provider:** Groq API (Llama/Mixtral vb. hızlı modeller için)
* **Veritabanı:** PostgreSQL / Local DB (Opsiyonel)
* **Altyapı & Dağıtım:** Docker & Docker Compose

## 🚀 Başlangıç (Getting Started)

Projeyi kendi bilgisayarınızda çalıştırmak için aşağıdaki adımları izleyin.

### Gereksinimler
- [Docker](https://www.docker.com/products/docker-desktop/) ve [Docker Compose](https://docs.docker.com/compose/)
- Groq API Anahtarı

### Kurulum Adımları

1. **Projeyi Klonlayın:**
   ```bash
   git clone https://github.com/kullaniciadi/aliagai.git
   cd aliagai
   ```

2. **Çevre Değişkenlerini Ayarlayın:**
   Ana dizinde bulunan `.env.example` dosyasını kopyalayarak `.env` adında yeni bir dosya oluşturun ve içine gerekli bilgileri girin:
   ```bash
   cp .env.example .env
   ```
   `.env` dosyanızı düzenleyin ve `GROQ_API_KEY` değerinizi ekleyin.

3. **Docker ile Uygulamayı Başlatın:**
   ```bash
   docker-compose up --build -d
   ```

4. **Kullanmaya Başlayın:**
   - API Dokümantasyonu (Swagger UI): `http://localhost:8000/docs`
   - Healthcheck: `http://localhost:8000/health`

## 📁 Dizin Yapısı

```text
aliagai/
├── backend/                # FastAPI backend uygulaması ve iş mantığı
├── frontend/               # Kullanıcı arayüzü (React/Next.js vb. - Geliştirme aşamasında)
├── memory-bank/            # Proje dokümantasyonu ve mimari notlar
├── logs/                   # Uygulama logları
├── docker-compose.yml      # Docker orkestrasyon dosyası
├── .env.example            # Örnek çevre değişkenleri
└── README.md               # Proje tanıtım dosyası
```

## 📈 Gelecek Planları (Roadmap)

- [ ] **Aşama 1 (MVP):** Aliağa için 220+ onaylı veri noktası ile çalışan, 3 sonuç kartı ve harita linki üreten temel sistem.
- [ ] **Aşama 2:** Menemen, Foça ve Karşıyaka gibi çevre ilçelere genişleme.
- [ ] **Aşama 3:** Esnaflar için premium profil ve öne çıkarma sistemi (Gelir Modeli).
- [ ] **Aşama 4:** "İlçemin Google'ı" vizyonuyla ulusal çapa yayılabilen SaaS platformu.

## 🤝 Katkıda Bulunma

Bu proje şu anda MVP aşamasında tek kişi tarafından geliştirilmektedir. Katkıda bulunmak isterseniz lütfen önce bir Issue açarak yapmak istediğiniz değişikliği tartışın.

## 📄 Lisans

Bu proje **MIT Lisansı** ile lisanslanmıştır. Daha fazla bilgi için `LICENSE` dosyasına göz atabilirsiniz.
