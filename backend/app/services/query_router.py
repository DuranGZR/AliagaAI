from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models import (
    PharmacyDuty, Place, PublicInstitution, HealthFacility, School,
    News, Announcement, Event, AntiqueCity, TourismSpot, Gastronomy,
    EmergencyPhone, Neighborhood, Hotel, Library,
)
from app.services.llm import LLMService
from app.services.rag import RAGService
import logging

logger = logging.getLogger(__name__)


class QueryRouter:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db
        self._llm = LLMService()
        self._rag = RAGService(db)

    async def process_query(self, query: str) -> dict:
        intent = await self._llm.classify_intent(query)
        intent_type = intent.get("intent", "hybrid")
        category = intent.get("category", "general")

        sql_results: list[dict] = []
        rag_results: list[dict] = []

        if intent_type in ("sql", "hybrid"):
            sql_results = await self._sql_search(category, intent.get("filters", {}))

        if intent_type in ("rag", "hybrid"):
            source_table = self._category_to_source_table(category)
            rag_results = await self._rag.search_similar(query, source_table=source_table)

        context = self._build_context(sql_results, rag_results)

        ai_response = ""
        if context.strip():
            ai_response = await self._llm.generate_response(query, context)

        return {
            "query": query,
            "intent": intent,
            "sql_results": sql_results,
            "rag_results": [
                {"content": r["content"], "similarity": round(r["similarity"], 3)}
                for r in rag_results
            ],
            "ai_response": ai_response,
            "result_count": len(sql_results) + len(rag_results),
        }

    async def _sql_search(self, category: str, filters: dict) -> list[dict]:
        handlers = {
            "pharmacy": self._search_pharmacies,
            "place": self._search_places,
            "institution": self._search_institutions,
            "tourism": self._search_tourism,
            "news": self._search_news,
            "event": self._search_events,
            "announcement": self._search_announcements,
        }

        handler = handlers.get(category)
        if handler:
            return await handler(filters)
        return []

    async def _search_pharmacies(self, filters: dict) -> list[dict]:
        stmt = select(PharmacyDuty).where(PharmacyDuty.duty_date == date.today())
        result = await self._db.execute(stmt)
        rows = result.scalars().all()
        return [
            {"type": "pharmacy", "name": r.name, "address": r.address, "phone": r.phone, "maps_link": r.maps_link}
            for r in rows
        ]

    async def _search_places(self, filters: dict) -> list[dict]:
        stmt = select(Place).where(Place.is_active.is_(True))
        if category_filter := filters.get("category"):
            stmt = stmt.where(Place.category == category_filter)
        stmt = stmt.order_by(Place.rating.desc().nullslast()).limit(10)
        result = await self._db.execute(stmt)
        rows = result.scalars().all()
        return [
            {
                "type": "place", "name": r.name, "category": r.category,
                "address": r.address, "phone": r.phone, "rating": r.rating,
                "maps_link": r.maps_link, "tags": r.tags,
            }
            for r in rows
        ]

    async def _search_institutions(self, filters: dict) -> list[dict]:
        results: list[dict] = []
        for Model, type_name in [
            (PublicInstitution, "public_institution"),
            (HealthFacility, "health_facility"),
            (School, "school"),
        ]:
            stmt = select(Model).limit(5)
            result = await self._db.execute(stmt)
            rows = result.scalars().all()
            for r in rows:
                results.append({
                    "type": type_name, "name": r.name,
                    "address": r.address, "phone": r.phone,
                })
        return results

    async def _search_tourism(self, filters: dict) -> list[dict]:
        results: list[dict] = []

        stmt = select(TourismSpot).limit(5)
        result = await self._db.execute(stmt)
        for r in result.scalars().all():
            results.append({"type": "tourism_spot", "name": r.name, "description": r.description, "address": r.address})

        stmt = select(AntiqueCity).limit(5)
        result = await self._db.execute(stmt)
        for r in result.scalars().all():
            results.append({"type": "antique_city", "name": r.name, "period": r.period, "description": r.description})

        return results

    async def _search_news(self, filters: dict) -> list[dict]:
        stmt = select(News).order_by(News.published_date.desc().nullslast()).limit(5)
        result = await self._db.execute(stmt)
        return [
            {"type": "news", "title": r.title, "summary": r.summary, "date": str(r.published_date)}
            for r in result.scalars().all()
        ]

    async def _search_events(self, filters: dict) -> list[dict]:
        stmt = (
            select(Event)
            .where(Event.event_date >= date.today())
            .order_by(Event.event_date.asc())
            .limit(5)
        )
        result = await self._db.execute(stmt)
        return [
            {
                "type": "event", "title": r.title, "date": str(r.event_date),
                "time": r.event_time, "location": r.location, "is_free": r.is_free,
            }
            for r in result.scalars().all()
        ]

    async def _search_announcements(self, filters: dict) -> list[dict]:
        stmt = select(Announcement).order_by(Announcement.published_date.desc().nullslast()).limit(5)
        result = await self._db.execute(stmt)
        return [
            {"type": "announcement", "title": r.title, "content": (r.content or "")[:300], "date": str(r.published_date)}
            for r in result.scalars().all()
        ]

    @staticmethod
    def _category_to_source_table(category: str) -> str | None:
        mapping = {
            "news": "news",
            "announcement": "announcements",
            "event": "events",
            "tourism": "tourism_spots",
            "general": None,
        }
        return mapping.get(category)

    @staticmethod
    def _build_context(sql_results: list[dict], rag_results: list[dict]) -> str:
        parts: list[str] = []

        if sql_results:
            for item in sql_results:
                line = " | ".join(f"{k}: {v}" for k, v in item.items() if v)
                parts.append(line)

        if rag_results:
            for item in rag_results:
                parts.append(item["content"])

        return "\n\n".join(parts)
