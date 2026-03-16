# AliağaAI - Aktif Bağlam

## 🎯 Şu Anki Odak: Mimari Değişim ve Sıfırdan Yapılanma
Proje önceden bir web uygulaması (opsiyonel frontend ile) olarak düşünülürken, güncel kararlarla birlikte **Mobil Uygulama (React Native)** odaklı, **Hibrit Arama (SQL + RAG)** mimarisine sahip bir sisteme dönüştürüldü.

Mevcut sistemin (FastAPI backend + basit LLM çağrısı vb.) işe yarar temel iskeletleri (örneğin Groq API entegrasyonu, loglama vs.) tutulacak, ancak Query Router, pgvector entegrasyonu ve React Native mobil uygulama yapıları için sıfırdan inşa süreçleri başlayacak.

## 📝 Son Yapılan Değişiklikler
*   Projenin temel amacı "Hibrit arama tabanlı mobil şehir rehberi" olarak güncellendi.
*   **Memory Bank (Proje Hafızası)** dokümanları (`projectbrief.md`, `productContext.md`, `systemPatterns.md`, `techContext.md`) baştan aşağıya yeni vizyona (Yıl Sonu Proje Sunumu PDF verilerine) uygun olarak yenilendi.
*   Teknoloji Yığını tamamen netleştirildi: **React Native, FastAPI, PostgreSQL + pgvector**.

## 🛠️ Sıradaki Adımlar (Next Steps)
1.  **Backend (FastAPI) Yeniden Yapılandırılması:**
    *   Mevcut backend içerisindeki yapıların yeni mimariye (Query Router) uygun hale getirilmesi.
    *   PostgreSQL ve `pgvector` bağlantılarının kurulması (SQLAlchemy + asyncpg).
    *   Veritabanı tablolarının (yapılandırılmış mekanlar) ve vektör tablolarının (RAG chunk'ları) oluşturulması.
2.  **Veri Toplama (Scraping) Modüllerinin Yazılması:**
    *   Belediye duyuruları, haberler ve eczaneler için otomatik scriptlerin yazılması.
    *   RAG için Data Ingestion pipeline'ının (Chunking + Embedding) kurulması.
3.  **Frontend (React Native) Temellerinin Atılması:**
    *   Expo veya React Native CLI kullanılarak projenin init edilmesi.
    *   Arama/Chat ekranı arayüzünün (UI) tasarlanması.
4.  **Admin Panel:**
    *   Manuel veri girişi için basit bir yönetim panelinin sisteme entegre edilmesi.

## ⚠️ Dikkat Edilecekler
*   AI kesinlikle karar verici değil, sadece **açıklayıcı** katman olarak çalışmalı. Query Router'ın (SQL mi RAG mı?) doğru ayrımı yapması sistemin en kritik noktasıdır.
*   Önceki sistemden kalan ve yeni `pgvector` & `React Native` vizyonuna uymayan kodlar tespit edilip temizlenecektir.
