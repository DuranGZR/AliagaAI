# AliağaAI - Proje Özeti

## 🎯 Proje Adı ve Tanımı
**AliağaAI**, Aliağa ilçesine ait yerel verileri kullanarak kullanıcıların sordukları sorulara hızlı ve güvenilir cevaplar veren **hibrit arama tabanlı bir mobil şehir rehberidir.**

Bu proje, kullanıcıların "Şu an açık nöbetçi eczane hangisi?", "Aliağa’da sakin bir restoran öner", "Bu hafta sonu etkinlik var mı?" gibi spesifik ve yerel bilgi arayışlarında yaşadığı erişim problemlerini çözmek amacıyla geliştirilmiştir. Genel arama motorlarının (Google vb.) karmaşıklığından ve reklamlarından arındırılmış, bağlama uygun ve doğru cevaplar üretir.

## ✅ Çözüm Yaklaşımı
*   **Aliağa’ya Özel Yerel Veri Tabanı:** Yalnızca ilçe sınırları içerisindeki veriler kullanılır.
*   **Kullanıcı Sorgularını Anlayan Arama Sistemi:** Doğal dildeki soruları anlama yeteneği.
*   **Hibrit Arama Mimarisi (SQL + RAG):** Sorunun türüne göre yapılandırılmış (SQL) veya metin tabanlı (RAG) arama.
*   **AI Karar Vermez, AI Açıklar:** Sistem veriyi bulur, yapay zeka sadece sonucu kullanıcıya anlaşılır şekilde anlatır. (Halüsinasyon riskini en aza indiren yaklaşım).
*   **Mobil Uygulama Odaklılık:** Kullanıcıların bilgiye her an hızlıca erişebilmesi için React Native tabanlı mobil uygulama.

## 📊 Veri Kaynakları ve Yönetimi
*   **Otomatik Veri (Scraping):** Belediye duyuruları, Nöbetçi eczaneler, Etkinlikler.
*   **Manuel Veri (Admin Panel):** Restoranlar, Kafeler, Turistik yerler.
*   **Admin Panel:** Mekân ekleme, veri düzenleme, kategori yönetimi ve içerik güncelleme işlemleri buradan yapılır.

## 🛠️ Temel Teknolojiler
*   **Mobil Uygulama:** React Native (iOS & Android)
*   **Backend Servisi:** Python FastAPI
*   **Veritabanı:** PostgreSQL
*   **Vektör Arama (Vector Search):** pgvector (RAG sistemi için)

## 🚀 Gelecek Planları (Roadmap)
*   Konum bazlı öneriler
*   Harita entegrasyonu
*   Kullanıcı yorum sistemi
*   Farklı ilçelere (Menemen, Foça, Karşıyaka vb.) genişleme
