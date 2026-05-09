from datetime import date, datetime, timedelta
import re
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime
from html import unescape
from urllib.parse import urlencode

import httpx
from bs4 import BeautifulSoup
from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.content import Obituary


TOKEN_URL = (
    "https://cbs.izmir.bel.tr/cbswebservisleri/CbsKurumSozelServisi/Mezarlik/"
    "mezarlikbilgisistemiservis.asmx/getToken?kontrol=88B20948-7F73-430F-8555-6F7BFFFD1FF4"
)
VEFAT_URL = (
    "https://cbs.izmir.bel.tr/cbswebservisleri/CbsKurumSozelServisi/Mezarlik/"
    "MezarlikBilgiSistemiServis.asmx/VefatBilgisiSorgula"
)


def _normalize_tr(text: str) -> str:
    value = (text or "").lower()
    table = str.maketrans("çğıöşü", "cgiosu")
    return value.translate(table)


def _extract_token(xml_text: str) -> str | None:
    m = re.search(r"([A-F0-9]{8}-[A-F0-9-]{27})", xml_text or "")
    return m.group(1) if m else None


def _extract_ilce(item: dict) -> str:
    for detail in (item.get("detayListesi") or []):
        if detail.get("key") == "mezarlikIlceAdi":
            return str(detail.get("value") or "")
    return ""


def _extract_date_from_pubdate(value: str | None) -> date | None:
    if not value:
        return None
    try:
        return parsedate_to_datetime(value).date()
    except Exception:
        return None


def _clean_html_text(value: str | None) -> str:
    if not value:
        return ""
    return " ".join(BeautifulSoup(unescape(value), "lxml").get_text(" ").split())


def _extract_name_from_title(title: str) -> str:
    # Ornek: "Hasan X Aliağa'da toprağa verildi"
    text = " ".join((title or "").split())
    patterns = [
        r"^(.+?)\s+hayatini\s+kaybetti",
        r"^(.+?)\s+vefat\s+etti",
        r"^(.+?)\s+topraga\s+verildi",
        r"^(.+?)\s+son\s+yolculuguna",
    ]
    n = _normalize_tr(text)
    for pat in patterns:
        m = re.search(pat, n)
        if m:
            # normalize tarafinda karakterler degistigi icin orijinalden yakalamayi tekrar dene
            original = text[: len(m.group(1))].strip(" -:,")
            if len(original) >= 3:
                return original[:255]

    # Kaynak adıyla biten başlıklarda yayıncıyı at
    if " - " in text:
        text = text.split(" - ")[0].strip()
    return text[:255]


def _looks_like_person_name(value: str) -> bool:
    text = " ".join((value or "").split()).strip()
    if len(text) < 5:
        return False
    parts = text.split(" ")
    if not (2 <= len(parts) <= 6):
        return False
    return all(len(p) >= 2 for p in parts)


class IzmirMezarlikScraper:
    """Izmir BSB servislerinden Aliağa odakli vefat kaydi ceker."""

    def __init__(self):
        self.timeout = 25

    async def _get_token(self) -> str | None:
        try:
            async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True, verify=False) as client:
                resp = await client.get(TOKEN_URL)
                resp.raise_for_status()
                return _extract_token(resp.text)
        except Exception as e:
            logger.warning(f"Mezarlik token alinamadi: {e}")
            return None

    async def _fetch_day(self, token: str, target_date: date) -> list[dict]:
        try:
            async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True, verify=False) as client:
                resp = await client.get(
                    VEFAT_URL,
                    params={"kontrol": token, "tarih": target_date.strftime("%Y-%m-%d")},
                )
                resp.raise_for_status()
                payload = resp.json()
                return payload.get("sonuc") or []
        except Exception:
            return []

    async def _save_record(
        self,
        session: AsyncSession,
        *,
        name: str,
        death_date: date | None,
        details: str,
        source: str,
        funeral_location: str | None = None,
        neighborhood: str | None = None,
    ) -> bool:
        if not name:
            return False

        existing = (
            await session.execute(
                select(Obituary).where(
                    Obituary.name == name[:255],
                    Obituary.death_date == death_date,
                )
            )
        ).scalars().first()
        if existing:
            return False

        session.add(
            Obituary(
                name=name[:255],
                death_date=death_date,
                funeral_time=None,
                funeral_location=(funeral_location or "Aliağa")[:255],
                neighborhood=(neighborhood[:100] if neighborhood else None),
                details=details[:5000],
                source=source[:255],
            )
        )
        return True

    async def fetch_obituaries(self, session: AsyncSession) -> int:
        """
        1) Resmi Izmir BSB vefat API'si
        2) Aliağa kaydi yoksa Google News RSS fallback
        """
        inserted = 0

        token = await self._get_token()
        if token:
            logger.info("Mezarlik API ile Aliağa vefat kayitlari kontrol ediliyor...")
            # Son 120 gun taraniyor; API 2026 verisinde bos ise fallback devreye girecek.
            for i in range(21):
                d = date.today() - timedelta(days=i)
                rows = await self._fetch_day(token, d)
                if not rows:
                    continue

                for row in rows:
                    ilce = _extract_ilce(row)
                    if "aliaga" not in _normalize_tr(ilce):
                        continue

                    name = str(row.get("adSoyad") or "").strip()
                    death_date = None
                    raw_date = str(row.get("vefatTarihi") or "")
                    m = re.search(r"(\d{1,2})/(\d{1,2})/(\d{4})", raw_date)
                    if m:
                        try:
                            death_date = datetime(int(m.group(3)), int(m.group(2)), int(m.group(1))).date()
                        except Exception:
                            death_date = d

                    details = " ".join(
                        x
                        for x in [
                            str(row.get("namazveDefinYeriBilgisi") or ""),
                            str(row.get("mezarlikBilgisi") or ""),
                            str(row.get("olumNedeni") or ""),
                        ]
                        if x
                    ).strip()
                    if not details:
                        details = f"{name} için Aliağa vefat kaydı"

                    saved = await self._save_record(
                        session,
                        name=name,
                        death_date=death_date or d,
                        details=details,
                        source="İzmir BSB Mezarlık Bilgi Sistemi",
                        funeral_location="Aliağa",
                        neighborhood=ilce,
                    )
                    if saved:
                        inserted += 1

        if inserted == 0:
            logger.info("Resmi API'den Aliağa vefat kaydi cikmadi; RSS fallback deneniyor...")
            inserted += await self._fetch_from_google_news(session)

        if inserted > 0:
            await session.commit()
            logger.info(f"Vefat: {inserted} yeni kayit eklendi.")
        else:
            logger.debug("Yeni vefat kaydi bulunamadi.")

        return inserted

    async def _fetch_from_google_news(self, session: AsyncSession) -> int:
        queries = [
            "Aliaga vefat",
            "Aliaga hayatini kaybetti",
            "Aliaga son yolculuguna ugurlandi",
        ]
        count = 0
        seen_urls: set[str] = set()

        async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True, verify=False) as client:
            for query in queries:
                url = "https://news.google.com/rss/search?" + urlencode(
                    {"q": query, "hl": "tr", "gl": "TR", "ceid": "TR:tr"}
                )
                try:
                    resp = await client.get(url)
                    resp.raise_for_status()
                    root = ET.fromstring(resp.text)
                except Exception as e:
                    logger.warning(f"RSS vefat sorgusu hatasi ({query}): {e}")
                    continue

                for item in root.findall(".//item")[:80]:
                    title = (item.findtext("title") or "").strip()
                    if not title:
                        continue

                    norm = _normalize_tr(title)
                    if "aliaga" not in norm:
                        continue
                    if not any(k in norm for k in ["vefat", "hayatini kaybet", "topraga ver", "son yolculu"]):
                        continue
                    if any(k in norm for k in ["su kesintisi", "elektrik kesintisi", "ihale", "kampanya"]):
                        continue

                    link = (item.findtext("link") or "").strip()
                    if link in seen_urls:
                        continue
                    seen_urls.add(link)

                    pub_date = _extract_date_from_pubdate(item.findtext("pubDate")) or date.today()
                    desc = _clean_html_text(item.findtext("description"))
                    full_details = " ".join(x for x in [title, desc, link] if x).strip()
                    name = _extract_name_from_title(title)
                    if not _looks_like_person_name(name):
                        continue

                    saved = await self._save_record(
                        session,
                        name=name,
                        death_date=pub_date,
                        details=full_details,
                        source="Google News RSS",
                        funeral_location="Aliağa",
                        neighborhood="Aliağa",
                    )
                    if saved:
                        count += 1

        return count

    async def scrape(self, **kwargs) -> list[dict]:
        return []


async def scrape_izmir_mezarlik(session: AsyncSession):
    scraper = IzmirMezarlikScraper()
    await scraper.fetch_obituaries(session)

