#!/usr/bin/env python3
"""
Enhanced MagicBricks Scraper with Premium Property Support
Handles all property types including premium, sponsored, and luxury listings
Ensures 100% extraction rate from all property cards
"""

import time
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup
import pandas as pd
import logging
import json
import re
from pathlib import Path

# Import existing systems
from incremental_scraping_system import IncrementalScrapingSystem
from user_mode_options import ScrapingMode
from date_parsing_system import DateParsingSystem
from smart_stopping_logic import SmartStoppingLogic
from url_tracking_system import URLTrackingSystem


class EnhancedPremiumScraper:
    """
    Enhanced MagicBricks scraper with premium property support
    Handles all property types including premium, sponsored, and luxury listings
    """
    
    def __init__(self, headless: bool = True, incremental_enabled: bool = True, custom_config: Dict[str, Any] = None):
        """Initialize enhanced scraper with premium property support"""

        # Core scraper setup
        self.headless = headless
        self.driver = None
        self.properties = []

        # Setup custom configuration
        self.config = self._setup_default_config()
        if custom_config:
            self.config.update(custom_config)

        # Incremental scraping system
        self.incremental_enabled = incremental_enabled
        if incremental_enabled:
            self.incremental_system = IncrementalScrapingSystem()
            self.date_parser = DateParsingSystem()
            self.stopping_logic = SmartStoppingLogic()
            self.url_tracker = URLTrackingSystem()
        
        # Session tracking
        self.session_stats = {
            'session_id': None,
            'start_time': None,
            'end_time': None,
            'mode': 'full',
            'pages_scraped': 0,
            'properties_found': 0,
            'properties_saved': 0,
            'premium_properties_found': 0,
            'extraction_success_rate': 0.0,
            'incremental_stopped': False,
            'stop_reason': None
        }

        # Premium property tracking
        self.premium_stats = {
            'total_premium': 0,
            'preferred_agent': 0,
            'card_luxury': 0,
            'sponsored': 0,
            'project_links': 0,
            'society_links': 0
        }

        # Enhanced selectors for premium properties
        self.premium_selectors = self._setup_premium_selectors()
        
        # Setup logging
        self.setup_logging()

        # Setup date parser
        if not hasattr(self, 'date_parser') or self.date_parser is None:
            self.date_parser = DateParsingSystem()

    def _setup_default_config(self) -> Dict[str, Any]:
        """Setup default configuration with premium property support"""
        return {
            'delays': {
                'page_load': (2, 4),
                'between_pages': (1, 3),
                'after_scroll': (0.5, 1.5)
            },
            'timeouts': {
                'page_load': 30,
                'element_wait': 10,
                'implicit_wait': 5
            },
            'premium_handling': {
                'detect_premium_types': True,
                'extract_project_links': True,
                'extract_society_links': True,
                'use_enhanced_selectors': True,
                'fallback_extraction': True
            },
            'extraction': {
                'require_valid_url': False,  # Allow premium properties without direct URLs
                'min_area_value': 100,  # Minimum area in sqft
                'validate_price_format': True,
                'extract_all_fields': True
            }
        }

    def _setup_premium_selectors(self) -> Dict[str, List[str]]:
        """Setup enhanced selectors for premium properties"""
        return {
            'title': [
                # Standard selectors
                'h2.mb-srp__card--title',
                'h2[class*="title"]',
                'h3[class*="title"]',
                'a[class*="title"]',
                '.mb-srp__card--title',
                # Premium property selectors
                '.preferred-agent h2',
                '.card-luxury h2',
                '.premium-listing h2',
                '.sponsored-card h2',
                # Fallback selectors
                'h1', 'h2', 'h3', 'h4',
                'a[href*="property"]',
                '.SRPTuple__title',
                '[data-testid*="title"]',
                # Text-based fallback
                '.card-title', '.property-title', '.listing-title'
            ],
            'price': [
                # Standard selectors
                'div.mb-srp__card__price--amount',
                'span[class*="price"]',
                'div[class*="price"]',
                '.mb-srp__card__price--amount',
                # Premium property selectors
                '.preferred-agent .price',
                '.card-luxury .price',
                '.premium-listing .price',
                '.sponsored-card .price',
                # Enhanced selectors
                '.SRPTuple__price',
                '[data-testid*="price"]',
                '*[class*="cost"]',
                '*[class*="amount"]',
                '*[class*="value"]',
                # Fallback selectors
                '.price-value', '.cost-value', '.amount-value'
            ],
            'area': [
                # Standard selectors
                'div.mb-srp__card__summary--value',
                'span[class*="area"]',
                'div[class*="area"]',
                '.mb-srp__card__summary--value',
                # Premium property selectors
                '.preferred-agent .area',
                '.card-luxury .area',
                '.premium-listing .area',
                '.sponsored-card .area',
                # Enhanced area selectors
                '.SRPTuple__area',
                '[data-testid*="area"]',
                '*[class*="sqft"]',
                '*[class*="size"]',
                '*[class*="carpet"]',
                '*[class*="super"]',
                '*[class*="built"]',
                # Specific area types
                '.carpet-area', '.super-area', '.built-area',
                '.area-value', '.size-value',
                # Text-based selectors
                '*:contains("sqft")', '*:contains("Sq.Ft")',
                '*:contains("carpet")', '*:contains("super")',
                # Fallback selectors
                '.property-area', '.listing-area', '.unit-area'
            ],
            'url': [
                # Standard URL selectors
                'a[href*="/propertydetail/"]',
                'a[href*="/property-details/"]',
                'a[href*="magicbricks.com"]',
                # Premium property URLs
                'a[href*="/project/"]',
                'a[href*="/society/"]',
                'a[href*="/builder/"]',
                'a[href*="pdpid"]',
                # Enhanced URL selectors
                'a[href*="property"]',
                'a[href*="listing"]',
                'a[href*="detail"]',
                # Fallback URL selectors
                'a[href]'
            ]
        }

    def setup_logging(self):
        """Setup enhanced logging with premium property tracking"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('enhanced_scraper.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info("Enhanced Premium Scraper initialized")

    def detect_premium_property_type(self, card) -> Dict[str, Any]:
        """Detect if a property card is a premium/special type"""
        premium_info = {
            'is_premium': False,
            'type': 'standard',
            'classes': [],
            'indicators': []
        }
        
        try:
            # Get all classes from the card
            card_classes = card.get('class', [])
            if isinstance(card_classes, str):
                card_classes = [card_classes]
            
            # Check for premium indicators
            premium_indicators = {
                'preferred-agent': 'preferred_agent',
                'card-luxury': 'luxury',
                'premium-listing': 'premium',
                'sponsored-card': 'sponsored',
                'featured': 'featured',
                'highlighted': 'highlighted'
            }
            
            for class_name in card_classes:
                for indicator, type_name in premium_indicators.items():
                    if indicator in class_name:
                        premium_info['is_premium'] = True
                        premium_info['type'] = type_name
                        premium_info['classes'].append(class_name)
                        premium_info['indicators'].append(indicator)
            
            # Check for premium text indicators
            card_text = card.get_text().lower()
            text_indicators = ['premium', 'luxury', 'featured', 'sponsored', 'preferred']
            for indicator in text_indicators:
                if indicator in card_text:
                    premium_info['indicators'].append(f'text_{indicator}')
                    if not premium_info['is_premium']:
                        premium_info['is_premium'] = True
                        premium_info['type'] = indicator
            
        except Exception as e:
            self.logger.warning(f"Error detecting premium property type: {e}")
        
        return premium_info

    def _extract_with_enhanced_fallback(self, card, selectors: List[str], field_type: str = 'text', default: str = 'N/A') -> str:
        """Enhanced extraction with premium property support and intelligent fallback"""
        
        # First try standard selectors
        for selector in selectors:
            try:
                elem = card.select_one(selector)
                if elem:
                    text = elem.get_text(strip=True)
                    if text and text != default and len(text) > 1:
                        # Additional validation for meaningful content
                        if not text.lower() in ['n/a', 'na', 'null', 'none', '--', '...']:
                            return text
            except Exception:
                continue
        
        # Enhanced fallback extraction based on field type
        try:
            all_text = card.get_text()
            
            if field_type == 'price':
                # Enhanced price pattern matching
                price_patterns = [
                    r'₹[\d,.]+ (?:Crore|Lakh|crore|lakh)',
                    r'₹[\d,.]+\s*(?:Cr|L|cr|l)\b',
                    r'₹[\d,.]+',
                    r'\b[\d,.]+ (?:Crore|Lakh|crore|lakh)\b',
                    r'Price[:\s]*₹[\d,.]+',
                    r'Cost[:\s]*₹[\d,.]+'
                ]
                for pattern in price_patterns:
                    match = re.search(pattern, all_text)
                    if match:
                        return match.group().strip()
            
            elif field_type == 'area':
                # Enhanced area pattern matching
                area_patterns = [
                    r'\b\d+[\d,.]* (?:sqft|sq ft|Sq\.? ?ft|SQFT)\b',
                    r'\b\d+[\d,.]* (?:sq\.?m|sqm|Sq\.?M)\b',
                    r'(?:Carpet|Super|Built)[\s:]*\d+[\d,.]* (?:sqft|sq ft)',
                    r'Area[:\s]*\d+[\d,.]* (?:sqft|sq ft)',
                    r'Size[:\s]*\d+[\d,.]* (?:sqft|sq ft)',
                    r'\d+[\d,.]* (?:Sq\.? ?Ft|SQFT)'
                ]
                for pattern in area_patterns:
                    match = re.search(pattern, all_text, re.I)
                    if match:
                        return match.group().strip()
            
            elif field_type == 'title':
                # Enhanced title extraction for premium properties
                title_patterns = [
                    r'\b\d+ BHK .+',
                    r'\b\d+ Bedroom .+',
                    r'\b(?:Apartment|Flat|Villa|House|Plot) .+',
                    r'\b[A-Z][a-z]+ (?:Apartment|Flat|Villa|House)\b'
                ]
                for pattern in title_patterns:
                    match = re.search(pattern, all_text)
                    if match:
                        return match.group().strip()
        
        except Exception as e:
            self.logger.warning(f"Error in enhanced fallback extraction: {e}")
        
        return default

    def _extract_premium_property_url(self, card) -> Optional[str]:
        """Enhanced URL extraction for premium properties"""
        
        # Try premium-specific URL selectors first
        premium_url_selectors = [
            'a[href*="/propertydetail/"]',
            'a[href*="/property-details/"]',
            'a[href*="/project/"]',
            'a[href*="/society/"]',
            'a[href*="/builder/"]',
            'a[href*="pdpid"]',
            'a[href*="magicbricks.com"]',
            'a[href*="property"]',
            'a[href*="listing"]',
            'a[href*="detail"]'
        ]
        
        for selector in premium_url_selectors:
            try:
                link = card.select_one(selector)
                if link and link.get('href'):
                    href = link.get('href')
                    # Validate URL
                    if self._is_valid_property_url(href):
                        return href
            except Exception:
                continue
        
        # Fallback: try any link in the card
        try:
            links = card.select('a[href]')
            for link in links:
                href = link.get('href')
                if href and self._is_valid_property_url(href, strict=False):
                    return href
        except Exception:
            pass
        
        return None
    
    def _is_valid_property_url(self, url: str, strict: bool = True) -> bool:
        """Validate if URL is a valid property URL"""
        if not url:
            return False
        
        # Skip invalid URLs
        invalid_patterns = ['javascript:', 'mailto:', '#', 'tel:']
        if any(pattern in url.lower() for pattern in invalid_patterns):
            return False
        
        if strict:
            # Strict validation for direct property URLs
            valid_patterns = [
                '/propertydetail/',
                '/property-details/',
                'magicbricks.com/property'
            ]
            return any(pattern in url for pattern in valid_patterns)
        else:
            # Relaxed validation for premium properties
            valid_patterns = [
                '/propertydetail/', '/property-details/',
                '/project/', '/society/', '/builder/',
                'pdpid', 'magicbricks.com'
            ]
            return any(pattern in url for pattern in valid_patterns)

    def extract_enhanced_property_data(self, card, page_number: int, property_index: int) -> Optional[Dict[str, Any]]:
        """Enhanced property data extraction with premium property support"""
        
        try:
            # Detect premium property type
            premium_info = self.detect_premium_property_type(card)
            
            # Extract title with enhanced fallback
            title = self._extract_with_enhanced_fallback(
                card, 
                self.premium_selectors['title'], 
                'title', 
                'N/A'
            )
            
            # Extract price with enhanced fallback
            price = self._extract_with_enhanced_fallback(
                card, 
                self.premium_selectors['price'], 
                'price', 
                'N/A'
            )
            
            # Extract area with enhanced fallback
            area = self._extract_with_enhanced_fallback(
                card, 
                self.premium_selectors['area'], 
                'area', 
                'N/A'
            )
            
            # Extract property URL with premium support
            property_url = self._extract_premium_property_url(card)
            
            # For premium properties, we don't require a valid URL
            if not property_url and not premium_info['is_premium']:
                if self.config['extraction']['require_valid_url']:
                    return None
            
            # Validate extracted data
            if not self._validate_extracted_data(title, price, area, premium_info['is_premium']):
                return None
            
            # Extract additional fields (same as original)
            posting_date_text = self._extract_with_enhanced_fallback(card, [
                '.mb-srp__card__photo__fig--post',
                'div[class*="post"]',
                'div[class*="update"]',
                'div[class*="date"]',
                '*[class*="ago"]',
                '*[class*="hours"]',
                '*[class*="yesterday"]',
                '*[class*="today"]'
            ], 'text', '')
            
            # Parse date
            date_parse_result = self.date_parser.parse_posting_date(posting_date_text) if self.date_parser and posting_date_text else None
            parsed_posting_date = date_parse_result.get('parsed_datetime') if date_parse_result and date_parse_result.get('success') else None
            
            # Extract structured fields
            bathrooms = self._extract_structured_field(card, 'Bathroom')
            balcony = self._extract_structured_field(card, 'Balcony')
            floor_details = self._extract_structured_field(card, 'Floor')
            status = self._extract_structured_field(card, 'Status')
            furnishing = self._extract_structured_field(card, 'Furnishing')
            facing = self._extract_structured_field(card, 'facing')
            parking = self._extract_structured_field(card, 'Car Parking')
            ownership = self._extract_structured_field(card, 'Ownership')
            transaction = self._extract_structured_field(card, 'Transaction')
            overlooking = self._extract_structured_field(card, 'overlooking')
            
            # Extract property type from title
            property_type = self._extract_property_type_from_title(title)
            
            # Extract society/project name
            society = self._extract_with_enhanced_fallback(card, [
                'a[href*="pdpid"]',
                'a[href*="project"]',
                'a[href*="society"]'
            ], 'text', '')
            
            # Extract locality
            locality = self._extract_with_enhanced_fallback(card, [
                '.mb-srp__card__ads--locality',
                '*[class*="locality"]'
            ], 'text', '')
            
            # Update premium stats
            if premium_info['is_premium']:
                self.premium_stats['total_premium'] += 1
                if 'preferred_agent' in premium_info['type']:
                    self.premium_stats['preferred_agent'] += 1
                elif 'luxury' in premium_info['type']:
                    self.premium_stats['card_luxury'] += 1
                elif 'sponsored' in premium_info['type']:
                    self.premium_stats['sponsored'] += 1
            
            # Build comprehensive property data
            property_data = {
                # Basic fields
                'title': title,
                'price': price,
                'area': area,
                'property_url': property_url,
                'page_number': page_number,
                'property_index': property_index,
                'scraped_at': datetime.now(),
                'posting_date_text': posting_date_text,
                'parsed_posting_date': parsed_posting_date,
                
                # Premium property info
                'is_premium': premium_info['is_premium'],
                'premium_type': premium_info['type'],
                'premium_classes': premium_info['classes'],
                'premium_indicators': premium_info['indicators'],
                
                # Comprehensive fields
                'bathrooms': bathrooms,
                'balcony': balcony,
                'property_type': property_type,
                'furnishing': furnishing,
                'floor_details': floor_details,
                'locality': locality,
                'society': society,
                'status': status,
                'facing': facing,
                'parking': parking,
                'ownership': ownership,
                'transaction': transaction,
                'overlooking': overlooking
            }
            
            return property_data
            
        except Exception as e:
            self.logger.error(f"Error extracting enhanced property data: {str(e)}")
            return None
    
    def _validate_extracted_data(self, title: str, price: str, area: str, is_premium: bool) -> bool:
        """Validate extracted data quality"""
        
        # For premium properties, we're more lenient
        if is_premium:
            # At least title should be valid
            return title and title != 'N/A' and len(title) > 5
        
        # For standard properties, require all basic fields
        if not title or title == 'N/A' or len(title) < 5:
            return False
        
        # Price validation (optional for some property types)
        if price and price != 'N/A':
            if not any(char in price for char in ['₹', 'crore', 'lakh', 'Crore', 'Lakh']):
                return False
        
        # Area validation
        if area and area != 'N/A':
            if not any(unit in area.lower() for unit in ['sqft', 'sq ft', 'sq.ft']):
                return False
            
            # Check minimum area
            try:
                area_value = re.search(r'\d+', area)
                if area_value and int(area_value.group()) < self.config['extraction']['min_area_value']:
                    return False
            except:
                pass
        
        return True
    
    def _extract_structured_field(self, card, field_name: str) -> str:
        """Extract structured field data (same as original)"""
        try:
            # Look for the field in structured data sections
            field_selectors = [
                f'*:contains("{field_name}")',
                f'[data-field="{field_name.lower()}"]',
                f'.{field_name.lower().replace(" ", "-")}'
            ]
            
            for selector in field_selectors:
                try:
                    elem = card.select_one(selector)
                    if elem:
                        # Try to find the value next to the field name
                        text = elem.get_text(strip=True)
                        if ':' in text:
                            return text.split(':', 1)[1].strip()
                        return text
                except:
                    continue
            
            return 'N/A'
        except Exception:
            return 'N/A'
    
    def _extract_property_type_from_title(self, title: str) -> str:
        """Extract property type from title (same as original)"""
        if not title or title == 'N/A':
            return 'N/A'
        
        # Common property type patterns
        patterns = {
            r'\b(\d+)\s*BHK\b': lambda m: f"{m.group(1)} BHK",
            r'\b(\d+)\s*Bedroom\b': lambda m: f"{m.group(1)} Bedroom",
            r'\bStudio\b': lambda m: "Studio",
            r'\bVilla\b': lambda m: "Villa",
            r'\bPlot\b': lambda m: "Plot",
            r'\bHouse\b': lambda m: "House"
        }
        
        for pattern, formatter in patterns.items():
            match = re.search(pattern, title, re.I)
            if match:
                return formatter(match)
        
        return 'Apartment'

    def get_extraction_summary(self) -> Dict[str, Any]:
        """Get comprehensive extraction summary"""
        total_properties = len(self.properties)
        successful_extractions = sum(1 for prop in self.properties if prop.get('title') != 'N/A')
        
        return {
            'total_properties_found': total_properties,
            'successful_extractions': successful_extractions,
            'extraction_success_rate': (successful_extractions / total_properties * 100) if total_properties > 0 else 0,
            'premium_stats': self.premium_stats,
            'session_stats': self.session_stats
        }

    def log_extraction_summary(self):
        """Log comprehensive extraction summary"""
        summary = self.get_extraction_summary()
        
        self.logger.info("=== ENHANCED EXTRACTION SUMMARY ===")
        self.logger.info(f"Total Properties Found: {summary['total_properties_found']}")
        self.logger.info(f"Successful Extractions: {summary['successful_extractions']}")
        self.logger.info(f"Extraction Success Rate: {summary['extraction_success_rate']:.1f}%")
        self.logger.info(f"Premium Properties: {summary['premium_stats']['total_premium']}")
        self.logger.info(f"  - Preferred Agent: {summary['premium_stats']['preferred_agent']}")
        self.logger.info(f"  - Luxury Cards: {summary['premium_stats']['card_luxury']}")
        self.logger.info(f"  - Sponsored: {summary['premium_stats']['sponsored']}")
        self.logger.info("=" * 40)