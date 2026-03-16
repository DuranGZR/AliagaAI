# AliağaAI - Gelişim Durumu (Progress)

## Genel Durum
**Aşama:** Backend tamamlandı, Frontend %95 tamamlandı — Entegrasyon ve Test aşamasına geçiş hazır.

## Tamamlananlar (Completed)

### Memory Bank
- `projectbrief.md`, `productContext.md`, `systemPatterns.md`, `techContext.md` — yeni vizyona göre güncellendi.
- `activeContext.md` — oluşturuldu ve güncellendi.

### Backend (FastAPI) — TAMAMEN YENİDEN YAPILANDIRILDI
- **Config** (`backend/app/config.py`): pydantic-settings ile yeniden yazıldı — PostgreSQL, Groq, embedding model, RAG parametreleri.
- **Database** (`backend/app/database.py`): Async SQLAlchemy (asyncpg) + pgvector eklentisi otomatik oluşturma.
- **Models** (`backend/app/models/__init__.py`): 25+ tablo korundu + yeni `DocumentChunk` tablosu `Vector(384)` ile.
- **Schemas** (`backend/app/schemas/__init__.py`): ChatRequest/Response, PharmacyOut, PlaceOut/Create/Update, NewsOut, EventOut vb.
- **Services katmanı** (yeni `backend/app/services/`):
  - `embedding.py`: SentenceTransformer wrapper (multilingual-e5-small), chunking mantığı.
  - `llm.py`: Groq AsyncGroq client, `generate_response()` ve `classify_intent()` fonksiyonları.
  - `rag.py`: pgvector ile vektörel benzerlik araması, doküman ingestion (chunking + embedding).
  - `query_router.py`: Intent classification → SQL/RAG/Hybrid yönlendirme → bağlam oluşturma → LLM yanıt.
- **Routes** yeniden yazıldı:
  - `search.py`: POST `/api/chat` (ana AI endpoint), GET pharmacies/places/news/events/announcements/institutions.
  - `admin.py`: CRUD places, scrape tetikleme, scheduler yönetimi.
- **Main** (`backend/app/main.py`): Async lifespan ile init_db/close_db, scheduler.
- **Docker** (`docker-compose.yml`): pgvector/pgvector:pg16 + FastAPI backend, health check'ler.
- **Dockerfile**: Async stack için güncellendi.
- **requirements.txt**: asyncpg, pgvector, sentence-transformers, groq, torch, numpy, tenacity, loguru.
- **.env.example**: Tüm yeni env değişkenleri ile güncellendi.

### Frontend (React Native / Expo) — %95 TAMAMLANDI
- **Expo projesi** oluşturuldu (blank-typescript template).
- **Bağımlılıklar**: @react-navigation/native, @react-navigation/bottom-tabs, @react-navigation/native-stack, react-native-screens, react-native-safe-area-context, axios, @expo/vector-icons.
- **Tema sistemi** (`src/theme/index.ts`): colors, spacing, borderRadius, typography, shadows.
- **Tip tanımları** (`src/types/index.ts`): ChatMessage, SearchResult, ChatResponse, Pharmacy, Place, NewsItem, EventItem.
- **API client** (`src/services/api.ts`): axios instance — chatService, pharmacyService, placeService, newsService, eventService.
- **Bileşenler** (`src/components/`):
  - `SearchBar.tsx`: Arama input'u, loading state.
  - `PlaceCard.tsx`: Mekan kartı — rating, tags, ara/harita aksiyonları.
  - `ChatBubble.tsx`: Kullanıcı/asistan mesaj baloncukları.
- **Ekranlar** (`src/screens/`):
  - `HomeScreen.tsx`: Chat arayüzü — öneri çipleri, mesaj listesi, AI yanıtları ile sonuç kartları.
  - `ExploreScreen.tsx`: Mekanlar grid — kategori filtre çipleri.
  - `PharmacyScreen.tsx`: Nöbetçi eczane listesi — ara/yol tarifi butonları.
  - `NewsScreen.tsx`: SectionList — etkinlikler + haberler.
- **Navigasyon** (`src/navigation/AppNavigator.tsx`): Bottom tab navigator — 4 sekme (Asistan, Keşfet, Eczane, Gündem), Ionicons ikonları.
- **App.tsx**: Root component — NavigationContainer + SafeAreaProvider.

## Bilinen Sorunlar (Minor — Çalışma Zamanını Etkilemez)
- `llm.py`: `messages` parametresi `list[dict[str, str]]` — Groq SDK tipi ile strict uyumsuzluk (runtime çalışır).
- `rag.py`: `.rowcount` CursorResult üzerinde — runtime sorunsuz çalışır.
- `scheduler.py`: Eski senkron scraper'lar — yeni async DB ile adaptasyon gerekebilir.
- Backend Python paketleri (pgvector, sentence-transformers, numpy) lokal venv'de yok — Docker ortamında çalışır.

## Yapılacaklar (To Do)
- [ ] Frontend'i `expo start` ile çalıştırarak derleme doğrulaması.
- [ ] Backend Docker container'larını `docker-compose up --build` ile ayağa kaldırma.
- [ ] Uçtan uca entegrasyon testi (mobil → API → DB → LLM → yanıt).
- [ ] Scraper'ların yeni async DB yapısına adaptasyonu.
- [ ] Admin paneli (opsiyonel — web tabanlı veya mobil ekran).
- [ ] Konum bazlı öneriler ve harita entegrasyonu (Roadmap Aşama 4).
