# AliağaAI - Gelişim Durumu (Progress)

## 📊 Genel Durum
**Aşama:** Yeni Mimariye Geçiş / Planlama (Yıl Sonu Sunumu vizyonuna adaptasyon)

Mevcut proje yapısı bir "Chatbot" konseptinden çıkartılarak "Hibrit Arama Tabanlı Mobil Şehir Rehberi" (React Native + FastAPI + pgvector) konseptine geçiş yapmıştır. Memory Bank tamamen güncellenmiştir. Geliştirme aşaması yeniden şekillendirilmektedir.

## 🟢 Tamamlananlar (Completed)
*   **Proje Vizyonunun Güncellenmesi:** Yeni PDF dökümanındaki sisteme göre proje kapsamı (Hibrit arama, SQL+RAG, mobil odaklılık) revize edildi.
*   **Memory Bank Güncellemesi:**
    *   `projectbrief.md` güncellendi (Mobil odak, hibrit yapı).
    *   `productContext.md` güncellendi (Problemler ve AI'ın açıklayıcı rolü).
    *   `systemPatterns.md` güncellendi (Query Router ve RAG mimarisi).
    *   `techContext.md` güncellendi (React Native, PostgreSQL, pgvector).
    *   `activeContext.md` oluşturuldu.

## 🟡 Devam Edenler (In Progress)
*   **Mevcut Kod Tabanının Temizlenmesi:** Backend (FastAPI) tarafında eski konseptten kalan kodların, yeni Query Router ve PostgreSQL yapısı için temizlenip yeniden yapılandırılması.
*   `docker-compose.yml` dosyasının PostgreSQL (pgvector eklentisiyle birlikte) destekleyecek şekilde güncellenmesi.

## 🔴 Yapılacaklar (To Do)
*   [ ] **Veritabanı Altyapısı:**
    *   Docker üzerinde `pgvector` içeren PostgreSQL imajının ayağa kaldırılması.
    *   Tablo şemalarının (Mekanlar, Kategoriler vb.) oluşturulması.
*   [ ] **Backend - Query Router:**
    *   Kullanıcı niyetini anlayan ve SQL / RAG ayrımını yapan yönlendirici fonksiyonunun yazılması.
*   [ ] **Backend - RAG Pipeline:**
    *   Veri toplama, temizleme, chunking ve embedding (vektörleştirme) servislerinin yazılması.
    *   Similarity search fonksiyonlarının geliştirilmesi.
*   [ ] **Frontend - Mobil Uygulama (React Native):**
    *   Projenin başlatılması (Expo vb. ile).
    *   API bağlantılarının kurulması.
    *   Arama/Chat UI tasarımının yapılması.
*   [ ] **Admin Panel:**
    *   Manuel veri girişi (Restoranlar, kafeler) için arayüz sağlanması.
