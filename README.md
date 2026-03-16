<div align="center">
  <h1>🌟 AliağaAI</h1>
  <p><b>Akıllı ve Hibrit Arama Tabanlı Mobil Şehir Rehberi</b></p>
  <p><i>Aliağa hakkında aradığınız her şeye, en doğru yerel veriler ve yapay zeka destekli açıklamalarla saniyeler içinde ulaşın.</i></p>

  <p>
    <img src="https://img.shields.io/badge/React_Native-20232A?style=for-the-badge&logo=react&logoColor=61DAFB" alt="React Native" />
    <img src="https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi" alt="FastAPI" />
    <img src="https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white" alt="PostgreSQL" />
    <img src="https://img.shields.io/badge/pgvector-000000?style=for-the-badge&logo=database&logoColor=white" alt="pgvector" />
    <img src="https://img.shields.io/badge/Groq-000000?style=for-the-badge&logo=groq&logoColor=white" alt="Groq" />
  </p>
</div>

<hr/>

## 🎯 Proje Hakkında

**AliağaAI**, İzmir'in Aliağa ilçesine ait yerel verileri kullanarak kullanıcıların sorularına hızlı ve güvenilir cevaplar veren **hibrit arama tabanlı bir mobil uygulamadır.** 

Geleneksel arama motorlarının (Google vb.) sunduğu karmaşık, reklamlı ve geniş çaplı sonuçlar yerine, yalnızca Aliağa'nın sınırları içerisindeki rafine verileri kullanarak çalışır. Sistem, "Nöbetçi eczane hangisi?", "Aileyle gidilecek restoran öner", "Belediye duyuruları neler?" gibi spesifik niyetleri anlar ve en doğru cevabı üretir.

> **Temel Prensibimiz (AI Karar Vermez, Açıklar):** Sistem arka planda hibrit arama (SQL + RAG) yaparak kesin ve doğru veriyi veritabanından çeker. Yapay zeka (LLM) ise sadece bu veriyi doğal, akıcı ve insani bir dille kullanıcıya aktarmak için kullanılır. Bu sayede AI "halüsinasyon" (uydurma) yapamaz.

## ✨ Öne Çıkan Özellikler

- **📱 Mobil Uygulama Deneyimi:** Her an elinizin altında olması için React Native ile geliştirilmiş iOS ve Android desteği.
- **🔀 Query Router (Akıllı Yönlendirme):** Kullanıcının sorusunu analiz ederek doğrudan yapılandırılmış veri mi (SQL) yoksa metin tabanlı bağlam araması mı (RAG) yapılacağına karar veren akıllı mekanizma.
- **🧠 Hibrit Arama (SQL + RAG):** PostgreSQL ile kesin eşleşmeler aranırken, `pgvector` ile haberler ve duyurular gibi metinler içinde vektörel (anlamsal) benzerlik araması yapılır.
- **🔄 Çift Yönlü Veri Kaynağı:** Belediye duyuruları, etkinlikler ve nöbetçi eczaneler web scraping ile **otomatik** güncellenirken; kafe, restoran gibi alanlar admin panelinden **manuel** yönetilir.

## 🛠️ Teknoloji Yığını

Sistem mimarisi performans, ölçeklenebilirlik ve mobil odaklılık üzerine kurulmuştur:

*   **Mobil Frontend:** React Native
*   **Backend & API:** Python (FastAPI)
*   **Veritabanı & Vektör Deposu:** PostgreSQL + `pgvector` eklentisi
*   **Yapay Zeka (LLM):** Groq API (Yüksek hızlı çıkarım - Llama/Mixtral vb.)
*   **Altyapı & Orkestrasyon:** Docker & Docker Compose

## 🏗️ Sistem Mimarisi

1. **Mobil Uygulama**, kullanıcıdan gelen soruyu backend'e iletir.
2. **Query Router**, sorunun tipini belirler:
   * *Açık Eczane:* Doğrudan **PostgreSQL (SQL)** sorgusu.
   * *Belediye Duyurusu:* Doğrudan **pgvector (RAG)** üzerinden benzerlik araması.
   * *Restoran Önerisi:* **Hibrit (SQL + AI)** filtreleme.
3. Bulunan veri, **LLM Servisine (Yapay Zeka)** gönderilir.
4. AI, veriyi kullanarak insani bir yanıt oluşturur ve mobil uygulamaya geri döner.

## 🚀 Başlangıç (Getting Started)

Uygulamanın arkaplan (backend ve veritabanı) servislerini yerel ortamınızda çalıştırmak için aşağıdaki adımları izleyin.

### Gereksinimler
- [Docker](https://www.docker.com/products/docker-desktop/) ve [Docker Compose](https://docs.docker.com/compose/)
- Groq API Anahtarı
- Node.js & npm / yarn (React Native tarafı için)

### Kurulum Adımları

1. **Projeyi Klonlayın:**
   ```bash
   git clone https://github.com/kullaniciadi/aliagai.git
   cd aliagai
   ```

2. **Backend ve Veritabanı Ayarları:**
   Ana dizindeki `.env.example` dosyasını `.env` olarak kopyalayın ve `GROQ_API_KEY` vb. ayarlarınızı yapın.
   ```bash
   cp .env.example .env
   ```

3. **Konteynerleri Başlatın (PostgreSQL, pgvector, FastAPI):**
   ```bash
   docker-compose up --build -d
   ```
   *Backend API Dokümantasyonuna şu adresten ulaşabilirsiniz:* `http://localhost:8000/docs`

4. **Mobil Uygulamayı Başlatın (Hazırlık Aşamasında):**
   *(React Native entegrasyonu tamamlandığında buraya Metro/Expo başlatma komutları eklenecektir.)*

## 📈 Gelecek Planları (Roadmap)

- [ ] **Aşama 1 (Core):** PostgreSQL + pgvector altyapısının Docker üzerinde ayağa kaldırılması ve FastAPI Query Router entegrasyonu.
- [ ] **Aşama 2 (Data):** Belediye siteleri ve eczaneler için Scraping (Veri çekme) ve RAG Chunking (Veri parçalama/vektörleme) sistemlerinin kurulması.
- [ ] **Aşama 3 (Mobile):** React Native mobil uygulamasının chat/arama arayüzlerinin tasarlanıp API'ye bağlanması.
- [ ] **Aşama 4 (Genişleme):** Konum bazlı öneriler, harita entegrasyonu ve Menemen, Foça gibi çevre ilçelere genişleme.

## 🤝 Katkıda Bulunma

Bu proje Aliağa'nın yerel bilgi ekosistemini iyileştirmek için geliştirilmektedir. Katkıda bulunmak isterseniz lütfen önce bir Issue açarak planlarınızı paylaşın.

## 📄 Lisans

Bu proje **MIT Lisansı** ile lisanslanmıştır. Detaylar için `LICENSE` dosyasına göz atabilirsiniz.
