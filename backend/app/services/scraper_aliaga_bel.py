from datetime import date, datetime
import re
from urllib.parse import urljoin, urlparse

from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.content import Announcement, JobListing, Project
from app.models.places import ServiceProvider
from app.services.scraper_base import BaseScraper


DATE_RE = re.compile(r"(\d{1,2}[./-]\d{1,2}[./-]\d{2,4})")


class AliagaBelScraper(BaseScraper):
    """Aliağa Belediyesi + İş'te Aliağa kaynaklarından içerik çeker."""

    def __init__(self):
        super().__init__()
        self.base_url = "https://www.aliaga.bel.tr"
        self.jobs_base_url = "https://www.istealiaga.com/"
        self.max_list_pages = 3

    def _to_absolute(self, href: str | None, base: str) -> str:
        if not href:
            return ""
        return urljoin(base, href).strip()

    @staticmethod
    def _slug_to_title(path: str) -> str:
        slug = path.rstrip("/").split("/")[-1]
        slug = re.sub(r"-\d+$", "", slug)
        return slug.replace("-", " ").strip().title()

    def _extract_main_text(self, soup, fallback: str = "") -> str:
        if not soup:
            return fallback
        for el in soup.select("script, style, nav, footer, header, .breadcrumb, .social-share"):
            el.decompose()

        blocks = []
        main = soup.select_one(".icerik, .content, .sayfa-content, article, main, .text")
        if main:
            blocks = [self.clean_text(p.get_text(" ")) for p in main.select("p, li")]
        else:
            blocks = [self.clean_text(p.get_text(" ")) for p in soup.select("p")]

        blocks = [b for b in blocks if len(b) >= 20]
        if blocks:
            return "\n".join(blocks[:8]).strip()

        body_text = self.clean_text(soup.get_text(" "))
        return body_text[:1200] if body_text else fallback

    @staticmethod
    def _extract_date_from_text(text: str | None) -> date | None:
        if not text:
            return None
        match = DATE_RE.search(text)
        if not match:
            return None
        value = match.group(1).replace("-", ".").replace("/", ".")
        parts = value.split(".")
        if len(parts) != 3:
            return None
        try:
            day, month, year = int(parts[0]), int(parts[1]), int(parts[2])
            if year < 100:
                year += 2000
            return datetime(year, month, day).date()
        except ValueError:
            return None

    async def fetch_projects(self, session: AsyncSession) -> int:
        """Tamamlanan/devam eden/sosyal proje detay linklerini çeker."""
        target_urls = [
            ("tamamlanan", f"{self.base_url}/projelerimiz/tamamlanan-projeler"),
            ("devam_eden", f"{self.base_url}/projelerimiz/devam-eden-projeler"),
            ("sosyal", f"{self.base_url}/projelerimiz/sosyal-sorumluluk-projeleri"),
        ]
        count = 0

        for status, url in target_urls:
            try:
                soup = await self._fetch_page(url)
                if not soup:
                    continue

                parent_path = urlparse(url).path.rstrip("/") + "/"
                seen_urls: set[str] = set()
                for a_tag in soup.find_all("a", href=True):
                    project_url = self._to_absolute(a_tag.get("href"), self.base_url)
                    parsed = urlparse(project_url)
                    if not project_url or parsed.netloc != "www.aliaga.bel.tr":
                        continue
                    if not parsed.path.startswith(parent_path):
                        continue
                    if parsed.path.rstrip("/") == parent_path.rstrip("/"):
                        continue
                    if project_url in seen_urls:
                        continue
                    seen_urls.add(project_url)

                    title = self.clean_text(a_tag.get_text())
                    if len(title) < 4:
                        title = self._slug_to_title(parsed.path)
                    if len(title) < 4:
                        continue

                    exists = (
                        await session.execute(
                            select(Project).where(Project.source_url == project_url)
                        )
                    ).scalars().first()
                    if exists:
                        continue

                    session.add(
                        Project(
                            title=title[:500],
                            description=f"Aliağa Belediyesi {status.replace('_', ' ')} projesi",
                            status=status,
                            source_url=project_url,
                        )
                    )
                    count += 1

            except Exception as e:
                logger.error(f"Projeler çekilirken hata ({url}): {e}")

        if count > 0:
            await session.commit()
            logger.info(f"Projeler: {count} yeni proje eklendi.")
        return count

    async def fetch_announcements(self, session: AsyncSession) -> int:
        """Duyuru ve ihale içeriklerini resmi listelerden çeker."""
        configs = [
            ("duyuru", f"{self.base_url}/duyurular", "/duyuru/"),
            ("ihale", f"{self.base_url}/ihaleler", "/ihale/"),
        ]
        count = 0

        for ann_type, base_list_url, detail_prefix in configs:
            seen_urls: set[str] = set()
            for page_idx in range(1, self.max_list_pages + 1):
                page_url = base_list_url if page_idx == 1 else f"{base_list_url}?page={page_idx}"
                soup = await self._fetch_page(page_url)
                if not soup:
                    continue

                for a_tag in soup.find_all("a", href=True):
                    detail_url = self._to_absolute(a_tag.get("href"), self.base_url)
                    parsed = urlparse(detail_url)
                    if parsed.netloc != "www.aliaga.bel.tr":
                        continue
                    if not parsed.path.startswith(detail_prefix):
                        continue
                    if detail_url in seen_urls:
                        continue
                    seen_urls.add(detail_url)

                    title = self.clean_text(a_tag.get_text())
                    if len(title) < 5:
                        title = self._slug_to_title(parsed.path)
                    if len(title) < 5:
                        continue

                    existing = (
                        await session.execute(
                            select(Announcement).where(Announcement.source_url == detail_url)
                        )
                    ).scalars().first()
                    if existing:
                        continue

                    detail_soup = await self._fetch_page(detail_url)
                    detail_text = self._extract_main_text(detail_soup, fallback=title)
                    published_at = self._extract_date_from_text(detail_text) or date.today()

                    session.add(
                        Announcement(
                            title=title[:500],
                            content=detail_text,
                            type=ann_type,
                            source_url=detail_url,
                            published_at=published_at,
                        )
                    )
                    count += 1

        if count > 0:
            await session.commit()
            logger.info(f"Duyuru/İhale: {count} yeni kayıt eklendi.")
        return count

    async def fetch_job_listings(self, session: AsyncSession) -> int:
        """İş'te Aliağa portalından aktif iş ilanlarını çeker."""
        listing_urls = [
            self.jobs_base_url,
            urljoin(self.jobs_base_url, "ilanlar"),
        ]
        count = 0
        seen_urls: set[str] = set()

        for listing_url in listing_urls:
            soup = await self._fetch_page(listing_url)
            if not soup:
                continue

            for a_tag in soup.find_all("a", href=True):
                href = a_tag.get("href")
                if not href or "is-ilani-" not in href:
                    continue

                detail_url = self._to_absolute(href, self.jobs_base_url)
                parsed = urlparse(detail_url)
                if parsed.netloc != "www.istealiaga.com":
                    continue
                if detail_url in seen_urls:
                    continue
                seen_urls.add(detail_url)

                title = self.clean_text(a_tag.get_text())
                if len(title) < 4:
                    title = self._slug_to_title(parsed.path)
                if len(title) < 4:
                    continue

                existing = (
                    await session.execute(
                        select(JobListing).where(JobListing.source_url == detail_url)
                    )
                ).scalars().first()
                if existing:
                    continue

                detail_soup = await self._fetch_page(detail_url)
                description = self._extract_main_text(detail_soup, fallback=title)
                company = "İş'te Aliağa"
                if detail_soup:
                    raw_text = self.clean_text(detail_soup.get_text(" "))
                    company_match = re.search(r"Firma\s*[:\-]\s*([^\n|,]{3,80})", raw_text, re.IGNORECASE)
                    if company_match:
                        company = self.clean_text(company_match.group(1))

                published_at = self._extract_date_from_text(description) or date.today()
                session.add(
                    JobListing(
                        title=title[:500],
                        company=company[:255] if company else None,
                        description=description,
                        source_url=detail_url,
                        published_at=published_at,
                        is_active=True,
                    )
                )
                count += 1

        if count > 0:
            await session.commit()
            logger.info(f"İş ilanları: {count} yeni ilan eklendi.")
        return count

    async def fetch_service_providers(self, session: AsyncSession) -> int:
        """Kent rehberi tablolarından telefonlu kurumsal/hizmet kayıtlarını çeker."""
        sources = [
            ("kamu", f"{self.base_url}/kent-rehberi/kamu-kuruluslari"),
            ("saglik", f"{self.base_url}/kent-rehberi/saglik-kuruluslari"),
            ("egitim", f"{self.base_url}/kent-rehberi/okullar"),
            ("muhtarlik", f"{self.base_url}/kent-rehberi/muhtarliklarimiz"),
        ]
        count = 0

        for category, source_url in sources:
            soup = await self._fetch_page(source_url)
            if not soup:
                continue

            for row in soup.select("table tr"):
                cells = [self.clean_text(cell.get_text(" ")) for cell in row.find_all(["th", "td"])]
                if len(cells) < 2:
                    continue

                raw = " ".join(cells).lower()
                if "telefon" in raw or "kurum" in raw or "okullar" in raw:
                    continue

                if category == "muhtarlik" and len(cells) >= 4:
                    name = f"{cells[0]} Muhtarlığı"
                    phone = cells[2]
                    address = cells[3]
                    neighborhood = cells[0]
                    description = f"{cells[1]} muhtar bilgisi."
                else:
                    name = cells[0]
                    phone = cells[1]
                    address = cells[2] if len(cells) >= 3 else None
                    neighborhood = None
                    description = f"Kent rehberi {category} kategorisinden çekildi."

                if len(name) < 3 or not re.search(r"\d", phone):
                    continue

                exists = (
                    await session.execute(
                        select(ServiceProvider).where(
                            ServiceProvider.name == name,
                            ServiceProvider.phone == phone,
                        )
                    )
                ).scalars().first()
                if exists:
                    continue

                session.add(
                    ServiceProvider(
                        name=name[:255],
                        phone=phone[:50],
                        category=category,
                        address=(address or "")[:1000] or None,
                        neighborhood=(neighborhood or None),
                        description=description,
                        is_24h=False,
                        is_active=True,
                    )
                )
                count += 1

        if count > 0:
            await session.commit()
            logger.info(f"Hizmet sağlayıcılar: {count} yeni kayıt eklendi.")
        return count

    async def scrape(self, **kwargs) -> list[dict]:
        return []


async def scrape_aliaga_bel_all(session: AsyncSession):
    scraper = AliagaBelScraper()
    await scraper.fetch_projects(session)
    await scraper.fetch_announcements(session)
    await scraper.fetch_job_listings(session)
    await scraper.fetch_service_providers(session)
