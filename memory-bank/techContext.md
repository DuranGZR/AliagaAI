# AliağaAI - Teknik Bağlam

Bu doküman, AliağaAI hibrit arama tabanlı mobil şehir rehberinin güncel teknoloji yığınını tanımlar.

## 📱 Frontend (Mobil Uygulama)
*   **Framework:** React Native
*   **Avantajı:** Tek bir kod tabanı (JavaScript/TypeScript) kullanarak hem iOS hem de Android için native benzeri performans sunan uygulamalar geliştirmeyi sağlar.

## ⚙️ Backend (API ve İş Mantığı)
*   **Dil:** Python
*   **Framework:** FastAPI
*   **Avantajı:** Asenkron (async/await) yapısıyla çok yüksek performans sunar. Özellikle API Gateway ve Query Router yapısı kurmak, AI modellerine istek atmak için Python ekosistemi idealdir.

## 🗄️ Veritabanı ve Vektör Arama
*   **İlişkisel Veritabanı:** PostgreSQL
*   **Vektör Veritabanı (RAG için):** pgvector eklentisi (PostgreSQL üzerinde)
*   **Avantajı:** Hem yapılandırılmış (SQL tabloları: mekanlar, eczaneler vb.) verileri hem de embedding vektörlerini (haberler, duyurular vb.) tek bir veritabanı altyapısında güvenli ve performanslı şekilde tutmayı sağlar. Ayrı bir vektör DB (Pinecone, Milvus vb.) ihtiyacını ortadan kaldırır.

## 🤖 Yapay Zeka (AI Katmanı)
*   **LLM API:** Groq (Llama / Mixtral modelleri) veya muadili hızlı LLM sağlayıcılar. AI sadece Query Router'dan veya RAG'dan dönen veriyi formatlayıp, açıklamakla yükümlüdür.
*   **Embedding Modelleri:** Metin verilerini vektörlere dönüştürmek için açık kaynaklı veya API tabanlı embedding modelleri (Örn: OpenAI `text-embedding-3-small`, BGE-M3 veya lokal sentence-transformers).

## 🛠️ Altyapı ve Diğer Araçlar
*   **Konteynerizasyon:** Docker & Docker Compose (Tüm yapıyı, özellikle PostgreSQL + pgvector kurulumunu kolaylaştırmak için).
*   **Veri Toplama (Scraping):** Python tabanlı araçlar (BeautifulSoup, Selenium vb. ile belediye sitesi ve eczane verilerini otomatik çekmek için).

## 🔀 Mimari Katmanlar
1.  **React Native** --> HTTPS/REST API İstekleri
2.  **FastAPI** --> API Endpoints & Query Router
3.  **PostgreSQL / pgvector** --> Veri Deposu (SQL & Vector Search)
4.  **LLM Service** --> Response Formatting
