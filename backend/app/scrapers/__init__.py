"""
AliağaAI Scraper Module
Aliağa Belediyesi web sitesinden veri çekmek için scraper'lar.
"""

from .base import BaseScraper
from .comprehensive import ComprehensiveScraper
from .dynamic import DynamicScraper

__all__ = [
    "BaseScraper",
    "ComprehensiveScraper",
    "DynamicScraper",
]
