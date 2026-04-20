"""
AliağaAI — Query Router (Sorgu Yönlendirici).

Sistemin beyni. Kullanıcı sorusunu analiz eder, en doğru SQL veya RAG sorgusunu çalıştırır
ve sonucu üretmesi için LLM'e bağlam (context) olarak iletir.
"""
from typing import Any
from datetime import date
from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.llm import get_json_response, generate_chat_response
from app.services.rag import search_similar_chunks
from app.schemas.chat import ChatResponse, SourceReference

from app.models.places import Pharmacy
from app.models.cache import (
    WeatherCache, PrayerTimesCache, FuelPricesCache,
    CurrencyCache, GoldCache, EarthquakesCache
)
from app.models.city import EmergencyContact, StreetMarket

# Intent analizi için kullanılacak prompt (Sistem yönergesi)
INTENT_SYSTEM_PROMPT = """Sen Aliağa yapay zeka şehir rehberisin. Gelen sorunun NİYETİNİ (intent) sınıflandırmalısın.
Seçebileceğin intentler ve kullanım alanları:
1. `pharmacy`: "Nöbetçi eczane hangisi?", "Bana en yakın eczane"
2. `weather`: "Hava nasıl?", "Yarın yağmur var mı?"
3. `prayer`: "Öğle ezanı ne zaman?", "İftar saat kaçta?"
4. `fuel`: "Benzin kaç para?", "Mazot fiyatları"
5. `currency`: "Dolar ne kadar?", "Euro kaç TL"
6. `gold`: "Gram altın", "Çeyrek fiyatı"
7. `earthquake`: "Az önce deprem mi oldu?", "Son depremler"
8. `emergency`: "Ambulans numarası", "İtfaiye telefon"
9. `market`: "Semt pazarı ne zaman?", "Hangi gün nerede pazar var?"
10. `place`: "Restoran önerisi", "Deniz kenarı kafe var mı?", "Antik kente nasıl giderim?"
11. `news`: "Son dakika haberler", "Belediyeden haberler"
12. `event`: "Bu hafta sonu etkinlik var mı?", "Tiyatro var mı?"
13. `general`: Aliağa hakkında genel bilgiler, tarihçe, nüfus veya yukarıdakilere uymayan her şey (RAG ile taranır).

SADECE ŞU JSON FORMATINDA YANIT VER:
{"intent": "<yukarıdaki_kelimelerden_biri>"}
"""

async def determine_intent(question: str) -> str:
    """Kullanıcı sorusundan LLM kullanarak intent (niyet) çıkarır."""
    messages = [
        {"role": "system", "content": INTENT_SYSTEM_PROMPT},
        {"role": "user", "content": question}
    ]
    response = await get_json_response(messages)
    return response.get("intent", "general")


async def execute_sql_query(session: AsyncSession, intent: str, query: str) -> dict:
    """Gerçek veritabanı tablolarına bağlanıp ilgili veriyi çeker."""
    data_str = ""
    sources_data = []

    if intent == "pharmacy":
        stmt = select(Pharmacy).where(Pharmacy.duty_date == date.today())
        result = await session.execute(stmt)
        pharmacies = result.scalars().all()
        if not pharmacies:
            data_str = "Bugün için nöbetçi eczane verisi bulunamadı."
        else:
            lines = [f"- {p.name} (Adres: {p.address}, Tel: {p.phone})" for p in pharmacies]
            data_str = "Bugünkü Nöbetçi Eczaneler:\n" + "\n".join(lines)
            sources_data.append(SourceReference(type="pharmacy", title="Bugünkü Nöbetçi Eczaneler"))

    elif intent == "weather":
        stmt = select(WeatherCache).order_by(WeatherCache.date.desc()).limit(1)
        result = await session.execute(stmt)
        weather = result.scalars().first()
        if not weather:
            data_str = "Güncel hava durumu verisi bulunamadı."
        else:
            data_str = f"Bugün hava {weather.temperature}°C, {weather.description}. Rüzgar: {weather.wind}, Nem: {weather.humidity}."
            sources_data.append(SourceReference(type="weather", title="Aliağa Hava Durumu"))

    elif intent == "prayer":
        stmt = select(PrayerTimesCache).order_by(PrayerTimesCache.date.desc()).limit(1)
        result = await session.execute(stmt)
        prayer = result.scalars().first()
        if not prayer:
            data_str = "Güncel namaz vakitleri bulunamadı."
        else:
            data_str = (
                f"Namaz Vakitleri:\n"
                f"İmsak: {prayer.fajr}\nGüneş: {prayer.sunrise}\nÖğle: {prayer.dhuhr}\n"
                f"İkindi: {prayer.asr}\nAkşam: {prayer.maghrib}\nYatsı: {prayer.isha}"
            )
            sources_data.append(SourceReference(type="prayer", title="Namaz Vakitleri"))

    elif intent == "fuel":
        stmt = select(FuelPricesCache).order_by(FuelPricesCache.fetched_at.desc()).limit(1)
        result = await session.execute(stmt)
        fuel = result.scalars().first()
        if not fuel:
            data_str = "Güncel akaryakıt verisi bulunamadı."
        else:
            data_str = f"Akaryakıt Fiyatları: Benzin {fuel.gasoline} TL, Motorin {fuel.diesel} TL, LPG {fuel.lpg} TL."
            sources_data.append(SourceReference(type="fuel", title="Akaryakıt Fiyatları"))

    elif intent == "currency":
        stmt = select(CurrencyCache)
        result = await session.execute(stmt)
        currencies = result.scalars().all()
        if not currencies:
            data_str = "Güncel döviz kurları bulunamadı."
        else:
            lines = [f"{c.name}: Alış {c.buying} TL, Satış {c.selling} TL" for c in currencies]
            data_str = "Güncel Döviz Kurları:\n" + "\n".join(lines)
            sources_data.append(SourceReference(type="currency", title="Döviz Kurları"))

    elif intent == "gold":
        stmt = select(GoldCache)
        result = await session.execute(stmt)
        golds = result.scalars().all()
        if not golds:
            data_str = "Güncel altın fiyatları bulunamadı."
        else:
            lines = [f"{g.name}: Alış {g.buying} TL, Satış {g.selling} TL" for g in golds]
            data_str = "Güncel Altın Fiyatları:\n" + "\n".join(lines)
            sources_data.append(SourceReference(type="gold", title="Altın Fiyatları"))

    elif intent == "earthquake":
        stmt = select(EarthquakesCache).order_by(EarthquakesCache.event_date.desc()).limit(5)
        result = await session.execute(stmt)
        quakes = result.scalars().all()
        if not quakes:
            data_str = "Deprem verisi bulunamadı."
        else:
            lines = [f"{q.magnitude} şiddetinde, {q.location} konumunda (Tarih: {q.event_date})" for q in quakes]
            data_str = "Geçmiş Son 5 Deprem:\n" + "\n".join(lines)
            sources_data.append(SourceReference(type="earthquake", title="Kandilli Rasathanesi Son Depremler"))

    elif intent == "emergency":
        stmt = select(EmergencyContact).order_by(EmergencyContact.priority.asc())
        result = await session.execute(stmt)
        contacts = result.scalars().all()
        if not contacts:
            data_str = "Acil durum numaraları bulunamadı."
        else:
            lines = [f"{c.name}: {c.phone}" for c in contacts]
            data_str = "Acil ve Önemli Numaralar:\n" + "\n".join(lines)
            sources_data.append(SourceReference(type="emergency", title="Acil Telefonlar"))

    elif intent == "market":
        stmt = select(StreetMarket)
        result = await session.execute(stmt)
        markets = result.scalars().all()
        if not markets:
            data_str = "Semt pazarı bilgisi bulunamadı."
        else:
            lines = [f"{m.name} - Gün: {m.day_of_week} ({m.neighborhood})" for m in markets]
            data_str = "Semt Pazarları ve Kuruldukları Günler:\n" + "\n".join(lines)
            sources_data.append(SourceReference(type="market", title="Semt Pazarları"))

    else:
        # Desteklenmeyen intent
        data_str = "İstenen veriye dair kategori eşleştirilemedi."

    return {"raw_data": data_str, "sources": sources_data}


async def process_chat_query(session: AsyncSession, user_message: str) -> ChatResponse:
    """
    Kullanıcı mesajının uçtan uca işlenmesi.
    1. Intent belirle
    2. SQL veya RAG ile veri topla
    3. LLM ile Türkçe ve dostane cevap üret
    """
    logger.info(f"YENİ SORGU: {user_message}")
    
    # 1. Intent belirleme
    intent = await determine_intent(user_message)
    logger.info(f"Tespit Edilen Intent: {intent}")
    
    search_method = "sql"
    context_data = ""
    sources = []

    # 2. Rota belirleme (SQL vs RAG)
    # Şimdilik SQL veya melez olanları ayırmadan RAG (pgvector) prototipi üzerinden geçiyoruz
    if intent in ["pharmacy", "weather", "prayer", "fuel", "currency", "gold", "earthquake", "emergency", "market"]:
        search_method = "sql"
        sql_result = await execute_sql_query(session, intent, user_message)
        context_data = sql_result["raw_data"]
    else:
        search_method = "rag" if intent == "general" else "hybrid"
        chunks = await search_similar_chunks(session, user_message, limit=5)
        
        if chunks:
            # Chunkları context olarak birleştir
            context_data = "\n\n".join([f"KAYNAK ({c['source_type']}): {c['content']}" for c in chunks])
            
            # Kaynakları formatla
            for c in chunks:
                sources.append(SourceReference(
                    type=c["source_type"],
                    title=c["metadata"].get("title", "Aliağa Bilgi Sayfası"),
                    url=c["metadata"].get("url")
                ))
        else:
            context_data = "Sistemde bu soruyla ilgili Aliağa'ya dair net bir bilgi bulunamadı."

    # 3. LLM ile Nihai Cevabı Üret
    GENERATION_PROMPT = f"""Sen AliağaAI'sın. Aliağa halkı için yerel ve akıllı bir şehir rehberisin.
Kullanıcının sorusuna SADECE aşağıda sağlanan "[BAĞLAM VERİSİ]" kısmındaki bilgilere dayanarak cevap ver.
Eğer bağlamda soruya uygun bir cevap yoksa, "Maalesef şu an bu bilgiye ulaşamıyorum" tarzında kibarca yanıt ver, ASLA kendin uydurma (halüsinasyon yapma).
Dostane, net ve yardımcı bir dil kullan. Uzatma.

[BAĞLAM VERİSİ BAŞLANGICI]
{context_data}
[BAĞLAM VERİSİ BİTİŞİ]
"""

    messages = [
        {"role": "system", "content": GENERATION_PROMPT},
        {"role": "user", "content": user_message}
    ]
    
    final_answer = await generate_chat_response(messages)
    if not final_answer:
        final_answer = "Şu an sistemimde bir sorun var, daha sonra tekrar deneyebilirsiniz."

    return ChatResponse(
        answer=final_answer,
        intent=intent,
        sources=sources,
        search_method=search_method
    )
