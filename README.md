# AliağaAI: Hibrit Arama Tabanlı Akıllı Şehir Rehberi

AliağaAI, Aliağa ilçesine özgü yerel verileri işleyerek kullanıcılara doğal dil üzerinden hızlı, güvenilir ve bağlamsal yanıtlar sunan gelişmiş bir asistan uygulamasıdır. Proje, genel arama motorlarının yerel veriye ulaşmadaki yetersizliğini ve reklam odaklı yapısını aşmak amacıyla, doğrudan kaynağını doğrulanmış yerel bilgilerden alan bir mimari üzerine kurulmuştur.

## Proje Vizyonu ve Kapsamı

Geleneksel arama algoritmaları, nöbetçi eczaneler, su kesintileri veya yerel etkinlikler gibi dinamik ve spesifik verilere erişimde çoğu zaman güncel olmayan veya alakasız sonuçlar üretmektedir. AliağaAI, bu problemi "Doğrulanmış Yerel Veri" ve "Yapay Zeka Destekli Hibrit Arama" yöntemleriyle çözer. Sistem, yapay zekayı bir karar verici olarak değil, veriyi bulan ve kullanıcıya insan dilinde özetleyen bir "sunum katmanı" olarak konumlandırır. Bu sayede halüsinasyon riski minimize edilir.

## Temel Özellikler

### Query Router (Sorgu Yönlendirici)
Sistemin kalbinde yer alan Query Router, kullanıcının sorduğu soruyu analiz ederek 25 farklı niyet (intent) arasından en uygun olanı seçer. Bu yönlendirme mekanizması, sorgunun türüne göre arama metodolojisini (SQL, RAG veya Hibrit) dinamik olarak belirler.

### Hibrit Veri Erişimi
- **Yapılandırılmış Veriler (SQL):** Eczaneler, namaz vakitleri ve akaryakıt fiyatları gibi kesin alanlara sahip veriler doğrudan ilişkisel veritabanı üzerinden çekilir.
- **Vektörel Veriler (Semantic Search):** Tarihçe, haber chunk'ları ve mekan açıklamaları gibi metin tabanlı veriler pgvector üzerinden semantik benzerlik algoritmalarıyla sorgulanır.
- **Hibrit Katman:** Mekan önerileri gibi hem konum/kategori filtresi hem de kullanıcı beklentisine uygun açıklama gerektiren sorgularda her iki katman birleştirilerek sonuç üretilir.

## Teknik Kurumsal Mimari

### Teknoloji Yığını
- **Backend:** Python FastAPI (Asenkron mimari, yüksek performanslı API Gateway)
- **Frontend:** React Native / Expo (Cross-platform mobil deneyimi)
- **Veritabanı:** PostgreSQL + pgvector (İlişkisel ve vektörel veriler için birleşik çözüm)
- **AI / LLM:** Groq Llama-3-70b (Hızlı çıkarım ve bağlam yönetimi)
- **Embedding:** Multilingual-E5-Small (Çok dilli metin vektörizasyonu)
- **Altyapı:** Docker & Docker Compose (Konteynerize dağıtım)

### Veri Katmanı Mimarisi
Sistem veri hassasiyetine göre üç farklı depolama stratejisi izler:

1.  **Strict SQL:** Sadece belirli filtrelerle çalışan veriler (Hava durumu, Depremler, Eczaneler).
2.  **SQL + pgvector:** Metaverisi olan ancak içeriği anlam araması gerektiren veriler (Haberler, Etkinlikler, Duyurular).
3.  **RAG Only:** Tamamen metin tabanlı şehir bilgisi ve statik dokümanlar.

## Sistem Akışı (Workflow)

Kullanıcı tarafından gönderilen her sorgu şu aşamalardan geçer:
1.  **Niyet Sınıflandırma:** Sorgu LLM aracılığıyla 25 ana kategoriden birine atanır.
2.  **Veri Elde Etme:** Belirlenen kategoriye göre ilgili SQL sorgusu veya Vektör benzerlik araması tetiklenir.
3.  **Bağlam Oluşturma:** Elde edilen ham veriler, sistem prompt'u ile birleştirilerek "Sadece bu verilere dayanarak cevap ver" talimatıyla LLM'e iletilir.
4.  **Yanıt Üretimi:** Kullanıcıya doğal bir dille formüle edilmiş, kaynak gösteren ve kart tabanlı görsellerle desteklenen yanıt sunulur.

## Kurulum ve Başlatma

### Ön Gereksinimler
- Docker ve Docker Compose
- Node.js (v18+) ve Expo CLI (Frontend geliştirme için)
- Python 3.9+ (Lokal backend geliştirme için)

### Backend Dağıtımı
Proje kök dizininde aşağıdaki komutu çalıştırarak tüm servisleri (PostgreSQL ve FastAPI) ayağa kaldırabilirsiniz:

```bash
docker-compose up -d
```

Servisler başladıktan sonra API dokümantasyonuna `http://localhost:8000/docs` adresinden erişilebilir.

### Frontend Kurulumu
Frontend bağımlılıklarını yüklemek ve uygulamayı başlatmak için:

```bash
cd frontend
npm install
npx expo start
```
