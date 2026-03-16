"""
Search Routes - Ana Arama API'si
"""

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from typing import List, Optional
from datetime import date
from sqlalchemy.orm import Session
import logging

from app.database import get_db
from app.models import PharmacyDuty, Institution, Place, KnowledgeBase

logger = logging.getLogger(__name__)
router = APIRouter()


# Response Models
class PharmacyResponse(BaseModel):
    id: int
    name: str
    address: Optional[str]
    phone: Optional[str]
    maps_link: Optional[str]
    
    class Config:
        from_attributes = True


class InstitutionResponse(BaseModel):
    id: int
    category: str
    name: str
    address: Optional[str]
    phone: Optional[str]
    maps_link: Optional[str]
    
    class Config:
        from_attributes = True


class PlaceResponse(BaseModel):
    id: int
    name: str
    category: Optional[str]
    address: Optional[str]
    phone: Optional[str]
    maps_link: Optional[str]
    rating: Optional[float]
    
    class Config:
        from_attributes = True


class SearchResponse(BaseModel):
    query: str
    results: List[dict]
    ai_summary: Optional[str] = None
    result_count: int


# Endpoints
@router.get("/pharmacies", response_model=List[PharmacyResponse])
async def get_pharmacies(
    db: Session = Depends(get_db),
    today_only: bool = Query(True, description="Sadece bugünkü nöbetçiler")
):
    """Nöbetçi eczaneleri getir"""
    query = db.query(PharmacyDuty)
    
    if today_only:
        query = query.filter(PharmacyDuty.duty_date == date.today())
    
    return query.all()


@router.get("/institutions", response_model=List[InstitutionResponse])
async def get_institutions(
    db: Session = Depends(get_db),
    category: Optional[str] = Query(None, description="Kategori filtresi")
):
    """Kamu kuruluşlarını getir"""
    query = db.query(Institution)
    
    if category:
        query = query.filter(Institution.category == category)
    
    return query.all()


@router.get("/institutions/categories")
async def get_institution_categories(db: Session = Depends(get_db)):
    """Kurum kategorilerini getir"""
    categories = db.query(Institution.category).distinct().all()
    return [c[0] for c in categories if c[0]]


@router.get("/places", response_model=List[PlaceResponse])
async def get_places(
    db: Session = Depends(get_db),
    category: Optional[str] = Query(None, description="Kategori filtresi"),
    limit: int = Query(10, le=50)
):
    """Mekanları getir"""
    query = db.query(Place)
    
    if category:
        query = query.filter(Place.category == category)
    
    return query.order_by(Place.rating.desc()).limit(limit).all()


@router.get("/knowledge/{topic}")
async def get_knowledge(
    topic: str,
    db: Session = Depends(get_db)
):
    """Belirli bir konu hakkında bilgi getir"""
    knowledge = db.query(KnowledgeBase).filter(
        KnowledgeBase.topic == topic
    ).first()
    
    if not knowledge:
        return {"topic": topic, "content": None, "found": False}
    
    return {
        "topic": knowledge.topic,
        "title": knowledge.title,
        "content": knowledge.content,
        "source_url": knowledge.source_url,
        "found": True
    }


@router.get("/knowledge")
async def list_knowledge_topics(db: Session = Depends(get_db)):
    """Mevcut bilgi konularını listele"""
    topics = db.query(KnowledgeBase.topic, KnowledgeBase.title).all()
    return [{"topic": t[0], "title": t[1]} for t in topics]


@router.get("/search", response_model=SearchResponse)
async def search(
    q: str = Query(..., min_length=2, description="Arama sorgusu"),
    db: Session = Depends(get_db)
):
    """
    Ana arama endpoint'i.
    Kullanıcı sorusuna göre en uygun sonuçları döndürür.
    """
    query_lower = q.lower()
    results = []
    
    # Anahtar kelime eşleştirme
    keyword_mapping = {
        "eczane": "pharmacy",
        "ilaç": "pharmacy",
        "nöbetçi": "pharmacy",
        "hastane": "institution_saglik",
        "sağlık": "institution_saglik",
        "doktor": "institution_saglik",
        "okul": "institution_okul",
        "lise": "institution_okul",
        "muhtar": "institution_muhtar",
        "acil": "institution_acil",
        "itfaiye": "institution_acil",
        "polis": "institution_acil",
        "ambulans": "institution_acil",
        "kafe": "place_kafe",
        "kahve": "place_kafe",
        "restoran": "place_restoran",
        "yemek": "place_restoran",
        "tarih": "knowledge_tarih",
        "antik": "knowledge_antik_kentler",
        "turizm": "knowledge_turizm",
        "gezi": "knowledge_gezilecek_yerler",
        "yemek": "knowledge_gastronomi",
        "kilim": "knowledge_helvaci_kilimi",
    }
    
    # Eşleşen kategorileri bul
    matched_type = None
    for keyword, result_type in keyword_mapping.items():
        if keyword in query_lower:
            matched_type = result_type
            break
    
    # Sonuçları getir
    if matched_type:
        if matched_type == "pharmacy":
            pharmacies = db.query(PharmacyDuty).filter(
                PharmacyDuty.duty_date == date.today()
            ).all()
            results = [
                {
                    "type": "pharmacy",
                    "name": p.name,
                    "address": p.address,
                    "phone": p.phone,
                    "maps_link": p.maps_link
                }
                for p in pharmacies
            ]
        
        elif matched_type.startswith("institution_"):
            category = matched_type.replace("institution_", "")
            institutions = db.query(Institution).filter(
                Institution.category == category
            ).limit(5).all()
            results = [
                {
                    "type": "institution",
                    "category": i.category,
                    "name": i.name,
                    "address": i.address,
                    "phone": i.phone,
                    "maps_link": i.maps_link
                }
                for i in institutions
            ]
        
        elif matched_type.startswith("place_"):
            category = matched_type.replace("place_", "")
            places = db.query(Place).filter(
                Place.category == category
            ).order_by(Place.rating.desc()).limit(3).all()
            results = [
                {
                    "type": "place",
                    "name": p.name,
                    "category": p.category,
                    "rating": p.rating,
                    "address": p.address,
                    "maps_link": p.maps_link
                }
                for p in places
            ]
        
        elif matched_type.startswith("knowledge_"):
            topic = matched_type.replace("knowledge_", "")
            knowledge = db.query(KnowledgeBase).filter(
                KnowledgeBase.topic == topic
            ).first()
            if knowledge:
                results = [{
                    "type": "knowledge",
                    "topic": knowledge.topic,
                    "title": knowledge.title,
                    "content": knowledge.content[:500] + "..." if len(knowledge.content) > 500 else knowledge.content
                }]
    
    # AI özet (şimdilik basit)
    ai_summary = None
    if results:
        if matched_type == "pharmacy":
            ai_summary = f"Bugün Aliağa'da {len(results)} nöbetçi eczane bulunuyor."
        elif matched_type and matched_type.startswith("institution_"):
            ai_summary = f"'{q}' araması için {len(results)} sonuç bulundu."
    
    return SearchResponse(
        query=q,
        results=results,
        ai_summary=ai_summary,
        result_count=len(results)
    )
