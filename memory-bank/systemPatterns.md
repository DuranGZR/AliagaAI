# AliağaAI - Sistem Mimarisi ve Tasarım Şablonları

## 🏗️ Genel Sistem Mimarisi

Sistem, bir mobil uygulama, bir backend servisi ve hibrit bir veri erişim katmanından oluşur. Sorgular, "Query Router" aracılığıyla uygun katmana yönlendirilir.

**Veri Akış Şeması:**
1. **Mobil Uygulama (React Native):** Kullanıcı sorguyu gönderir (HTTPS / REST).
2. **API Gateway / Backend (FastAPI):** Sorguyu karşılar ve iş mantığına iletir.
3. **Query Router:** Sorguyu analiz edip "Yapılandırılmış Arama (SQL)" mı yoksa "Metin Tabanlı Arama (RAG)" mı yapılacağına karar verir.
4. **Veri Getirme:**
   *   **Path A (Structured Search):** Doğrudan PostgreSQL üzerinden klasik veritabanı sorgusu.
   *   **Path B (RAG Pipeline):** Sorgu embedding'e dönüştürülüp `pgvector` üzerinden benzer vektörler taranır.
5. **LLM Service:** Bulunan veriler bağlam olarak LLM'e (Yapay Zeka) sunulur. LLM sadece bu verileri yorumlar ve cevap üretir ("AI karar vermez, AI açıklar").
6. **Response Formatter:** LLM cevabını ve referans verilerini (harita linki, mekan detayları) derler.
7. **Client Response:** Kullanıcıya dönen JSON yanıt.

## 🔀 Query Router (Sorgu Yönlendirici) Şablonu

En kritik bileşen, maliyeti düşürmek ve doğruluğu artırmak için çalışan Query Router'dır. Her sorgu LLM'e doğrudan gitmez, arama stratejisi belirlenir.

*   **SQL (Structured Search):** Doğrudan eşleşen ve yapılandırılmış verilere ihtiyaç duyan sorgular (Örn: "Şu an açık nöbetçi eczane hangisi?").
*   **SQL + AI:** Yarı yapılandırılmış verilerin veya filtrelerin, zenginleştirilmiş yanıtlarla sunulması (Örn: "Restoran önerisi").
*   **RAG (Retrieval-Augmented Generation):** Bağlam gerektiren, metinlerin içinde anlamsal arama yapılması gereken durumlar (Örn: "Belediye duyuruları neler?", "Hafta sonu etkinlikleri").

## 🧠 RAG (Retrieval-Augmented Generation) Mimarisi

RAG süreci iki ana aşamadan oluşur:

### 1. Hazırlık Süreci (Data Ingestion)
1.  **Ham Metin Verisi:** Haberler, duyurular vs. toplanır.
2.  **Ön İşleme:** Gereksiz HTML tag'leri, linkler vb. temizlenir.
3.  **Chunking:** Metin anlamlı boyutlara bölünür.
4.  **Embedding Modeli:** Parçalar vektörlere dönüştürülür.
5.  **Vektör Deposu:** PostgreSQL üzerinde `pgvector` eklentisiyle tablolanır.

### 2. Sorgu Süreci (Query & Response)
1.  **Kullanıcı Sorusu:** RAG'a düşen soru alınır.
2.  **Sorgu Embedding'i:** Kullanıcı sorusu aynı modelle vektöre dönüştürülür.
3.  **Benzer Chunkların Getirilmesi:** Vector Search yapılarak en alakalı K adet chunk veritabanından çekilir.
4.  **Bağlam Oluşturma:** Sorulan soru ve alakalı chunk'lar bir "prompt" içerisinde birleştirilir.
5.  **LLM (Yapay Zeka):** Sadece verilen bağlama dayanarak yanıt üretmesi istenir (Prompt Engineering ile halüsinasyon engellenir).
6.  **Yanıt:** Mobil uygulamaya sunulur.

## 🛡️ AI'ın Sınırları ("Yalnızca Açıklama" Katmanı)

Sistemde LLM'in tek rolü: Gelen ham, doğru veriyi insan diline çevirmek ve özetlemektir.

*   **Yasaklananlar:** Sistem dışında bilgi üretmesi, internette güncel arama yapıp onu cevaplaması (kendi bilgisiyle cevap vermesi yasaktır).
*   **İzin Verilenler:** "Bulunan mekanların adresini, neden listeye alındığını (açık olduğu için vb.) ve özelliklerini kullanıcıya derli toplu açıklamak."
