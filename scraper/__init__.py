"""
MagicBricks Scraper Package
Modular scraper components for better maintainability and testability
"""

from .property_extractor import PropertyExtractor
from .bot_detection_handler import BotDetectionHandler
from .export_manager import ExportManager
from .data_validator import DataValidator
from .individual_property_scraper import IndividualPropertyScraper

__all__ = [
    'PropertyExtractor',
    'BotDetectionHandler',
    'ExportManager',
    'DataValidator',
    'IndividualPropertyScraper'
]

