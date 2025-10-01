#!/usr/bin/env python3
"""
Property Data Extractor Module
Handles all property data extraction logic from listing pages and individual property pages.
Extracted from integrated_magicbricks_scraper.py for better maintainability.
"""

import re
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from bs4 import BeautifulSoup


class PropertyExtractor:
    """
    Comprehensive property data extraction with premium property support
    and intelligent fallback strategies
    """
    
    def __init__(self, premium_selectors: Dict[str, List[str]], date_parser=None, logger=None):
        """
        Initialize property extractor
        
        Args:
            premium_selectors: Dictionary of premium property selectors
            date_parser: Date parsing system instance
            logger: Logger instance
        """
        self.premium_selectors = premium_selectors
        self.date_parser = date_parser
        self.logger = logger or logging.getLogger(__name__)
        
        # Extraction statistics
        self.extraction_stats = {
            'total_extracted': 0,
            'successful_extractions': 0,
            'failed_extractions': 0,
            'premium_properties': 0,
            'standard_properties': 0
        }
    
    def extract_property_data(self, card, page_number: int, property_index: int) -> Optional[Dict[str, Any]]:
        """Enhanced property data extraction with premium property support"""
        
        try:
            # Update extraction stats
            self.extraction_stats['total_extracted'] += 1
            
            # Detect premium property type
            premium_info = self.detect_premium_property_type(card)
            
            if premium_info['is_premium']:
                self.extraction_stats['premium_properties'] += 1
            else:
                self.extraction_stats['standard_properties'] += 1
            
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
            
            # More lenient validation - save properties with partial data
            has_title = title and title != 'N/A' and len(title.strip()) > 3
            has_price = price and price != 'N/A' and len(price.strip()) > 1
            has_area = area and area != 'N/A' and len(area.strip()) > 1
            
            # For premium properties, be very lenient
            if premium_info['is_premium']:
                is_valid = has_title or has_price or has_area
            else:
                # For standard properties, require at least title OR (price AND area)
                is_valid = has_title or (has_price and has_area)
            
            if not is_valid:
                self.extraction_stats['failed_extractions'] += 1
                return None
            
            # Extract posting date
            posting_date_text = self._extract_with_fallback(card, [
                '.mb-srp__card__photo__fig--post',
                'div[class*="post"]',
                'div[class*="update"]',
                'div[class*="date"]',
                '*[class*="ago"]',
                '*[class*="hours"]',
                '*[class*="yesterday"]',
                '*[class*="today"]'
            ], '')
            
            # Parse date if parser available
            if not posting_date_text and self.date_parser:
                card_text = card.get_text()
                posting_date_text = self.date_parser.parse_posting_date(card_text)
            
            date_parse_result = self.date_parser.parse_posting_date(posting_date_text) if self.date_parser and posting_date_text else None
            parsed_posting_date = date_parse_result.get('parsed_datetime') if date_parse_result and date_parse_result.get('success') else None
            
            # Extract structured property details
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
            society = self._extract_society_enhanced(card)
            
            # Extract locality
            locality = self._extract_locality_enhanced(card)
            
            # Extract missing high-priority fields
            photo_count = self._extract_with_fallback(card, [
                '.mb-srp__card__photo__fig--count',
                '*[class*="photo"][class*="count"]'
            ], '')
            
            owner_name = self._extract_with_fallback(card, [
                '.mb-srp__card__ads--name',
                '*[class*="owner"]',
                '*[class*="ads"][class*="name"]'
            ], '')
            
            contact_options = self._extract_contact_options(card)
            description = self._extract_description(card)
            
            # Create enhanced description if none found
            if not description or len(description.strip()) == 0:
                description = self._create_enhanced_description_from_data(
                    title, price, area, locality, society, status
                )
            
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
                
                # Premium property information
                'is_premium': premium_info['is_premium'],
                'premium_type': premium_info['premium_type'],
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
                'overlooking': overlooking,
                
                # Phase 3 Enhancement fields
                'photo_count': photo_count,
                'owner_name': owner_name,
                'contact_options': contact_options,
                'description': description
            }
            
            # Update successful extraction stats
            self.extraction_stats['successful_extractions'] += 1
            
            return property_data
            
        except Exception as e:
            self.extraction_stats['failed_extractions'] += 1
            self.logger.error(f"Error extracting property data: {str(e)}")
            return None
    
    def detect_premium_property_type(self, card) -> Dict[str, Any]:
        """Detect if a property card is a premium/special type"""
        premium_info = {
            'is_premium': False,
            'premium_type': 'standard',
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
                'card--premium': 'premium',
                '--premium': 'premium',
                'sponsored-card': 'sponsored',
                '--sponsored': 'sponsored',
                'featured': 'featured',
                'highlighted': 'highlighted'
            }
            
            for class_name in card_classes:
                for indicator, type_name in premium_indicators.items():
                    if indicator in class_name:
                        premium_info['is_premium'] = True
                        premium_info['premium_type'] = type_name
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
                        premium_info['premium_type'] = indicator
            
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
                    r'(?:Apartment|House|Villa|Plot) .+',
                    r'[A-Z][a-z]+ [A-Z][a-z]+ .+'
                ]
                for pattern in title_patterns:
                    match = re.search(pattern, all_text)
                    if match:
                        return match.group().strip()

        except Exception:
            pass

        return default

    def _extract_with_fallback(self, card, selectors: List[str], default: str = 'N/A') -> str:
        """Extract text using fallback selectors with intelligent filtering"""

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

        # If no specific selector works, try intelligent text extraction
        try:
            all_text = card.get_text()

            # Look for price patterns
            if any(keyword in selectors[0].lower() for keyword in ['price', 'cost', 'amount']):
                price_match = re.search(r'₹[\d,.]+ (?:Crore|Lakh|crore|lakh)', all_text)
                if price_match:
                    return price_match.group()

            # Look for area patterns
            if any(keyword in selectors[0].lower() for keyword in ['area', 'sqft', 'size']):
                area_match = re.search(r'\d+[\d,.]* (?:sqft|sq ft|Sq\.? ?ft)', all_text, re.I)
                if area_match:
                    return area_match.group()

        except Exception:
            pass

        return default

    def _extract_premium_property_url(self, card) -> str:
        """Extract property URL with premium property support"""
        url_selectors = self.premium_selectors.get('url', [])

        # Try premium selectors first
        for selector in url_selectors:
            try:
                elem = card.select_one(selector)
                if elem and elem.get('href'):
                    url = elem.get('href')
                    if self._is_valid_property_url(url):
                        # Convert relative URLs to absolute
                        if url.startswith('/'):
                            url = f"https://www.magicbricks.com{url}"
                        return url
            except Exception:
                continue

        # Fallback: try any link in the card that might be valid
        try:
            all_links = card.select('a[href]')
            for link in all_links:
                url = link.get('href', '')
                if url and self._is_valid_property_url(url):
                    # Convert relative URLs to absolute
                    if url.startswith('/'):
                        url = f"https://www.magicbricks.com{url}"
                    return url
        except Exception:
            pass

        return ''

    def _is_valid_property_url(self, url: str) -> bool:
        """Validate if URL is a valid property URL"""
        if not url:
            return False

        # Skip invalid URLs
        invalid_patterns = ['javascript:', 'mailto:', '#', 'tel:', 'void(0)']
        if any(pattern in url.lower() for pattern in invalid_patterns):
            return False

        # Check for valid property URL patterns (updated for 2025)
        valid_patterns = [
            'pdpid',  # Most common current pattern
            'property-detail',
            'propertyDetails',
            'property-details',
            '/property/',
            'propertydetail',
            'magicbricks.com',
            # Location-based patterns
            '-gurgaon-',
            '-mumbai-',
            '-delhi-',
            '-bangalore-',
            '-pune-',
            '-hyderabad-',
            '-chennai-',
            '-kolkata-'
        ]

        return any(pattern in url for pattern in valid_patterns)

    def _extract_structured_field(self, card, field_name: str) -> str:
        """Enhanced structured field extraction with multiple strategies"""
        try:
            # Strategy 1: Find all elements that contain the field name
            field_elements = card.find_all(text=lambda text: text and field_name.lower() in text.lower())

            for element in field_elements:
                # Get the parent element
                parent = element.parent
                if parent:
                    # Look for the next sibling or child that contains the value
                    next_sibling = parent.find_next_sibling()
                    if next_sibling:
                        value = next_sibling.get_text(strip=True)
                        if value and value != field_name and len(value) > 0:
                            return value

                    # Look for value in the same parent element
                    parent_text = parent.get_text(strip=True)
                    if ':' in parent_text:
                        parts = parent_text.split(':')
                        if len(parts) >= 2:
                            value = parts[1].strip()
                            if value and len(value) > 0:
                                return value

            # Strategy 2: Look for field-specific patterns
            if field_name.lower() == 'status':
                return self._extract_status_enhanced(card)

            # Strategy 3: Look in all text for field patterns
            all_text = card.get_text()

            # Pattern: "Field: Value" or "Field - Value"
            pattern = rf'{re.escape(field_name)}\s*[:\-]\s*([^\n,]+)'
            match = re.search(pattern, all_text, re.IGNORECASE)
            if match:
                value = match.group(1).strip()
                if value and len(value) > 0:
                    return value

            return ''
        except Exception:
            return ''

    def _extract_property_type_from_title(self, title: str) -> str:
        """Extract property type from title (1 BHK, 2 BHK, Studio, etc.)"""
        try:
            # Look for BHK patterns
            bhk_match = re.search(r'(\d+)\s*BHK', title, re.I)
            if bhk_match:
                return f"{bhk_match.group(1)} BHK"

            # Look for Studio
            if 'studio' in title.lower():
                return 'Studio'

            # Look for other property types
            property_types = ['Villa', 'House', 'Plot', 'Apartment', 'Flat']
            for prop_type in property_types:
                if prop_type.lower() in title.lower():
                    return prop_type

            return ''
        except Exception:
            return ''

    def _extract_contact_options(self, card) -> str:
        """Extract contact options (Contact Owner, Get Phone No., etc.)"""
        try:
            contact_buttons = []

            # Look for contact action buttons
            contact_selectors = [
                '.mb-srp__action--btn',
                '*[class*="action"][class*="btn"]',
                '*[class*="contact"]',
                '*[class*="phone"]'
            ]

            for selector in contact_selectors:
                elements = card.select(selector)
                for elem in elements:
                    text = elem.get_text(strip=True)
                    if text and any(keyword in text.lower() for keyword in ['contact', 'phone', 'call', 'get']):
                        if text not in contact_buttons:
                            contact_buttons.append(text)

            return ', '.join(contact_buttons) if contact_buttons else ''

        except Exception:
            return ''

    def _extract_description(self, card) -> str:
        """Extract property description with enhanced fallback strategies"""
        try:
            # Strategy 1: Look for actual description paragraphs
            all_paragraphs = card.find_all('p')

            for p in all_paragraphs:
                text = p.get_text(strip=True)

                # Look for meaningful descriptions (longer than 50 characters)
                if text and len(text) > 50:
                    # Remove "Read more" if present
                    text = text.replace('Read more', '').strip()

                    # Skip common non-description text patterns
                    skip_patterns = [
                        'contact', 'phone', 'owner:', 'photos', 'updated', 'posted',
                        'premium member', 'newly launched', 'get phone', 'call now'
                    ]

                    # Check if this is likely a description
                    text_lower = text.lower()
                    is_description = any(keyword in text_lower for keyword in [
                        'bhk', 'apartment', 'flat', 'house', 'property', 'sale', 'resale',
                        'located', 'situated', 'available', 'gurgaon', 'sector'
                    ])

                    # Skip if it contains non-description patterns
                    has_skip_pattern = any(skip in text_lower for skip in skip_patterns)

                    if is_description and not has_skip_pattern:
                        # Clean up the text
                        text = text.replace('..', '.').strip()
                        return text[:500]  # Limit to 500 characters

            return ''

        except Exception:
            return ''

    def _extract_locality_enhanced(self, card) -> str:
        """Enhanced locality extraction with multiple strategies"""
        try:
            # Strategy 1: Look for explicit locality elements
            locality_selectors = [
                '.mb-srp__card__ads--locality',
                '*[class*="locality"]',
                '*[class*="location"]',
                '*[class*="address"]',
                '*[class*="area"]'
            ]

            for selector in locality_selectors:
                elements = card.select(selector)
                for elem in elements:
                    text = elem.get_text(strip=True)
                    if text and len(text) > 3 and len(text) < 100:  # Reasonable locality length
                        # Skip if it's clearly not a locality
                        if not any(skip in text.lower() for skip in ['contact', 'phone', 'owner', 'photos', 'bhk', 'sqft']):
                            return text

            # Strategy 2: Extract from title (many titles contain locality info)
            title_elem = card.select_one('h2, h3, .mb-srp__card__title, *[class*="title"]')
            if title_elem:
                title = title_elem.get_text(strip=True)

                # Pattern for "in [Locality] [City]"
                locality_pattern = r'in\s+([^,]+?)(?:\s+(?:Gurgaon|Noida|Mumbai|Delhi|Bangalore|Pune|Chennai|Hyderabad))'
                match = re.search(locality_pattern, title, re.IGNORECASE)
                if match:
                    locality = match.group(1).strip()
                    if len(locality) > 3 and len(locality) < 50:
                        return locality

                # Pattern for "Sector XX" or similar
                sector_pattern = r'(Sector\s+\d+[A-Z]*)'
                match = re.search(sector_pattern, title, re.IGNORECASE)
                if match:
                    return match.group(1)

            # Strategy 3: Look in all text for locality indicators
            all_text = card.get_text()
            locality_indicators = ['Sector', 'Block', 'Phase', 'Extension', 'Colony', 'Nagar', 'Vihar']

            for indicator in locality_indicators:
                if indicator in all_text:
                    # Extract surrounding text
                    pattern = rf'({indicator}\s+[A-Z0-9]+[A-Z]*)'
                    match = re.search(pattern, all_text, re.IGNORECASE)
                    if match:
                        return match.group(1)

            return ''

        except Exception:
            return ''

    def _extract_society_enhanced(self, card) -> str:
        """Enhanced society/project name extraction"""
        try:
            # Strategy 1: Look for project/society links
            link_selectors = [
                'a[href*="pdpid"]',  # Project detail page links
                'a[href*="project"]',
                '*[class*="society"]',
                '*[class*="project"]',
                '*[class*="building"]'
            ]

            for selector in link_selectors:
                elements = card.select(selector)
                for elem in elements:
                    text = elem.get_text(strip=True)
                    if text and len(text) > 3 and len(text) < 100:
                        # Skip if it's clearly not a society name
                        if not any(skip in text.lower() for skip in ['contact', 'phone', 'owner', 'photos', 'bhk', 'sqft', 'for sale']):
                            return text

            # Strategy 2: Extract from URL if available
            url_elem = card.select_one('a[href*="magicbricks.com"]')
            if url_elem:
                href = url_elem.get('href', '')
                if href:
                    # Extract society name from URL
                    url_pattern = r'magicbricks\.com/([^-]+(?:-[^-]+)*)-(?:sector|block|phase)'
                    match = re.search(url_pattern, href, re.IGNORECASE)
                    if match:
                        society_name = match.group(1).replace('-', ' ').title()
                        if len(society_name) > 3:
                            return society_name

            # Strategy 3: Look for society names in title
            title_elem = card.select_one('h2, h3, .mb-srp__card__title, *[class*="title"]')
            if title_elem:
                title = title_elem.get_text(strip=True)

                # Enhanced society name patterns
                society_patterns = [
                    # Brand-specific patterns
                    r'(DLF\s+[A-Za-z0-9\s]+)',
                    r'(Ansal\s+[A-Za-z0-9\s]+)',
                    r'(ROF\s+[A-Za-z0-9\s]+)',
                    r'(Tulip\s+[A-Za-z0-9\s]+)',
                    r'(Hero\s+[A-Za-z0-9\s]+)',
                    r'(Southend\s+[A-Za-z0-9\s]+)',
                    r'(Godrej\s+[A-Za-z0-9\s]+)',
                    r'(Tata\s+[A-Za-z0-9\s]+)',
                    r'(Emaar\s+[A-Za-z0-9\s]+)',
                    r'(M3M\s+[A-Za-z0-9\s]+)',

                    # Generic patterns
                    r'([A-Z][a-z]+\s+(?:Heights|Towers|Residency|Apartments|Homes|Gardens|Park|Plaza|Complex|Floors|Enclave|City|County|Estate))',

                    # Pattern for "Name Sector" format
                    r'([A-Z][A-Za-z\s]+)\s+(?:Sector|Block|Phase)\s+\d+',

                    # Pattern for society names before "in"
                    r'(?:in\s+)?([A-Z][A-Za-z\s]{3,30}?)\s+(?:Sector|Block|Phase)',
                ]

                for pattern in society_patterns:
                    match = re.search(pattern, title, re.IGNORECASE)
                    if match:
                        society_name = match.group(1).strip()
                        if len(society_name) > 3 and len(society_name) < 50:
                            return society_name

            return ''

        except Exception:
            return ''

    def _extract_status_enhanced(self, card) -> str:
        """
        Enhanced multi-level status extraction with comprehensive fallback strategy
        Target: Improve status extraction from 76% to 92%+

        Strategy:
        1. Direct selector-based extraction
        2. Text pattern matching with regex
        3. Keyword-based inference from description
        4. Contextual inference from other fields
        """
        try:
            # LEVEL 1: Direct selector-based extraction
            # Try multiple selector patterns for status field
            status_selectors = [
                '.mb-srp__card__summary__list--value',  # Primary selector
                'span[class*="status"]',
                'div[class*="status"]',
                'span[class*="possession"]',
                'div[class*="possession"]',
                '*[class*="ready"]',
                '*[class*="construction"]',
                '*[data-label*="status" i]',
                '*[data-label*="possession" i]'
            ]

            for selector in status_selectors:
                elements = card.select(selector)
                for elem in elements:
                    # Check if this element or its parent contains "status" or "possession"
                    elem_text = elem.get_text(strip=True).lower()
                    parent_text = elem.parent.get_text(strip=True).lower() if elem.parent else ''

                    # Look for status-related labels
                    if any(keyword in parent_text for keyword in ['status', 'possession', 'ready']):
                        text = elem.get_text(strip=True)
                        if text and 3 < len(text) < 50:
                            # Validate it's a status value, not a label
                            if not any(label in text.lower() for label in ['status:', 'possession:', 'label']):
                                return self._normalize_status(text)

            # LEVEL 2: Text pattern matching with comprehensive regex patterns
            all_text = card.get_text()

            # Pattern 1: "Status: Ready to Move" or "Possession: Dec 2024"
            status_patterns = [
                r'Status[:\s]+([A-Za-z\s]+(?:to\s+Move|Construction|Launch|Resale))',
                r'Possession[:\s]+([A-Za-z]+\s+\d{4})',
                r'Possession[:\s]+(Immediate|Ready|Available)',
                r'Ready\s+to\s+Move',
                r'Under\s+Construction',
                r'New\s+Launch',
                r'Resale',
                r'Immediate\s+Possession',
                r'Possession\s+by\s+([A-Za-z]+\s+\d{4})',
                r'Available\s+from\s+([A-Za-z]+\s+\d{4})'
            ]

            for pattern in status_patterns:
                match = re.search(pattern, all_text, re.IGNORECASE)
                if match:
                    status_text = match.group(1) if match.lastindex else match.group(0)
                    return self._normalize_status(status_text)

            # LEVEL 3: Keyword-based inference from description
            # Look for status keywords in the full card text
            all_text_lower = all_text.lower()

            # Define status keywords with priority (most specific first)
            status_keywords = [
                ('ready to move', 'Ready to Move'),
                ('ready for possession', 'Ready to Move'),
                ('immediate possession', 'Immediate Possession'),
                ('under construction', 'Under Construction'),
                ('new launch', 'New Launch'),
                ('new project', 'New Launch'),
                ('resale', 'Resale'),
                ('pre-launch', 'Pre-Launch'),
                ('nearing completion', 'Under Construction'),
            ]

            for keyword, normalized_status in status_keywords:
                if keyword in all_text_lower:
                    return normalized_status

            # LEVEL 4: Contextual inference from other fields
            # Check for possession date patterns
            possession_date_pattern = r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}'
            if re.search(possession_date_pattern, all_text, re.IGNORECASE):
                match = re.search(possession_date_pattern, all_text, re.IGNORECASE)
                if match:
                    return f"Possession: {match.group(0)}"

            # Check for "new" indicators
            if any(indicator in all_text_lower for indicator in ['newly built', 'brand new', 'new property']):
                return 'New Launch'

            # Check for "resale" indicators
            if any(indicator in all_text_lower for indicator in ['resale property', 'second sale', 'pre-owned']):
                return 'Resale'

            # LEVEL 5: Default fallback
            # If no status found, return empty string (will be marked as N/A in final data)
            return ''

        except Exception as e:
            # Log error but don't fail the extraction
            return ''

    def _normalize_status(self, status_text: str) -> str:
        """Normalize status text to standard format"""
        if not status_text:
            return ''

        status_lower = status_text.lower().strip()

        # Normalize to standard status values
        if 'ready' in status_lower and 'move' in status_lower:
            return 'Ready to Move'
        elif 'ready' in status_lower or 'immediate' in status_lower:
            return 'Ready to Move'
        elif 'under construction' in status_lower or 'construction' in status_lower:
            return 'Under Construction'
        elif 'new launch' in status_lower or 'new project' in status_lower:
            return 'New Launch'
        elif 'resale' in status_lower:
            return 'Resale'
        elif 'pre-launch' in status_lower or 'pre launch' in status_lower:
            return 'Pre-Launch'
        elif 'possession' in status_lower:
            # Keep possession dates as-is
            return status_text.strip()
        else:
            # Return as-is if it's a valid status
            return status_text.strip()

    def _create_enhanced_description_from_data(self, title, price, area, locality, society, status) -> str:
        """Create enhanced description from extracted property data"""
        try:
            description_parts = []

            # Add title if available
            if title and len(title.strip()) > 0:
                description_parts.append(title.strip())

            # Add price if available
            if price and len(price.strip()) > 0:
                description_parts.append(f"Priced at {price.strip()}")

            # Add area if available
            if area and len(area.strip()) > 0:
                description_parts.append(f"Area: {area.strip()}")

            # Add status if available
            if status and len(status.strip()) > 0:
                description_parts.append(f"Status: {status.strip()}")

            # Add locality if available
            if locality and len(locality.strip()) > 0:
                description_parts.append(f"Located in {locality.strip()}")

            # Add society if available
            if society and len(society.strip()) > 0:
                description_parts.append(f"Project: {society.strip()}")

            # Combine into meaningful description
            if len(description_parts) >= 2:  # At least title + one detail
                enhanced_description = '. '.join(description_parts)
                return enhanced_description[:500]  # Limit to 500 characters

            return ''

        except Exception:
            return ''

    # ========== INDIVIDUAL PROPERTY PAGE EXTRACTION METHODS ==========

    def _safe_extract_property_title(self, soup: BeautifulSoup) -> str:
        """Safely extract property title from individual page with fallbacks"""
        selectors = [
            'h1.mb-ldp__dtls__title',
            'h1[class*="title"]',
            '.property-title',
            'h1',
            '[class*="heading"]',
            '[class*="name"]'
        ]

        for selector in selectors:
            try:
                element = soup.select_one(selector)
                if element:
                    title = element.get_text(strip=True)
                    if title and len(title) > 5:  # Ensure meaningful title
                        return title
            except Exception as e:
                self.logger.debug(f"Error extracting title with selector {selector}: {str(e)}")
                continue

        return ''

    def _safe_extract_property_price(self, soup: BeautifulSoup) -> str:
        """Safely extract property price from individual page with fallbacks"""
        selectors = [
            '.mb-ldp__dtls__price',
            '[class*="price"]',
            '.property-price',
            '[class*="cost"]',
            '[class*="amount"]'
        ]

        for selector in selectors:
            try:
                element = soup.select_one(selector)
                if element:
                    price = element.get_text(strip=True)
                    # Validate price format (should contain numbers and currency indicators)
                    if price and any(char.isdigit() for char in price):
                        return price
            except Exception as e:
                self.logger.debug(f"Error extracting price with selector {selector}: {str(e)}")
                continue

        return ''

    def _safe_extract_property_area(self, soup: BeautifulSoup) -> str:
        """Safely extract property area from individual page with fallbacks"""
        selectors = [
            '.mb-ldp__dtls__area',
            '[class*="area"]',
            '.property-area',
            '[class*="sqft"]',
            '[class*="size"]'
        ]

        for selector in selectors:
            try:
                element = soup.select_one(selector)
                if element:
                    area = element.get_text(strip=True)
                    # Validate area format (should contain numbers and area units)
                    if area and any(char.isdigit() for char in area):
                        return area
            except Exception as e:
                self.logger.debug(f"Error extracting area with selector {selector}: {str(e)}")
                continue

        return ''

    def _safe_extract_amenities(self, soup: BeautifulSoup) -> List[str]:
        """Safely extract amenities from individual page with fallbacks"""
        amenities = []

        amenity_selectors = [
            '.mb-ldp__amenities li',
            '.amenities-list li',
            '[class*="amenity"]',
            '[class*="facility"] li',
            '[class*="feature"] li'
        ]

        for selector in amenity_selectors:
            try:
                elements = soup.select(selector)
                for element in elements:
                    amenity = element.get_text(strip=True)
                    if amenity and len(amenity) > 2 and amenity not in amenities:
                        amenities.append(amenity)
            except Exception as e:
                self.logger.debug(f"Error extracting amenities with selector {selector}: {str(e)}")
                continue

        return amenities

    def _safe_extract_description(self, soup: BeautifulSoup) -> str:
        """Safely extract property description from individual page with fallbacks"""
        selectors = [
            '.mb-ldp__dtls__desc',
            '.property-description',
            '[class*="description"]',
            '[class*="about"]',
            '[class*="detail"] p'
        ]

        for selector in selectors:
            try:
                element = soup.select_one(selector)
                if element:
                    description = element.get_text(strip=True)
                    if description and len(description) > 20:  # Ensure meaningful description
                        return description
            except Exception as e:
                self.logger.debug(f"Error extracting description with selector {selector}: {str(e)}")
                continue

        return ''

    def _safe_extract_builder_info(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Safely extract builder information from individual page with fallbacks"""
        builder_info = {}

        builder_selectors = [
            '.mb-ldp__builder__name',
            '.builder-name',
            '[class*="builder"]',
            '[class*="developer"]'
        ]

        for selector in builder_selectors:
            try:
                element = soup.select_one(selector)
                if element:
                    name = element.get_text(strip=True)
                    if name and len(name) > 2:
                        builder_info['name'] = name
                        break
            except Exception as e:
                self.logger.debug(f"Error extracting builder info with selector {selector}: {str(e)}")
                continue

        return builder_info

    def _safe_extract_location_details(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Safely extract detailed location information with fallbacks"""
        location_details = {}

        location_selectors = [
            '.mb-ldp__location',
            '.property-location',
            '[class*="location"]',
            '[class*="address"]'
        ]

        for selector in location_selectors:
            try:
                element = soup.select_one(selector)
                if element:
                    address = element.get_text(strip=True)
                    if address and len(address) > 5:
                        location_details['address'] = address
                        break
            except Exception as e:
                self.logger.debug(f"Error extracting location with selector {selector}: {str(e)}")
                continue

        return location_details

    def _safe_extract_specifications(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Safely extract detailed specifications with fallbacks"""
        specifications = {}

        spec_selectors = [
            '.mb-ldp__specs tr',
            '.specifications tr',
            '[class*="spec"] tr',
            '[class*="detail"] tr'
        ]

        for selector in spec_selectors:
            try:
                rows = soup.select(selector)
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 2:
                        key = cells[0].get_text(strip=True)
                        value = cells[1].get_text(strip=True)
                        if key and value and len(key) > 1 and len(value) > 1:
                            specifications[key] = value
            except Exception as e:
                self.logger.debug(f"Error extracting specifications with selector {selector}: {str(e)}")
                continue

        return specifications

    def get_extraction_statistics(self) -> Dict[str, int]:
        """Get current extraction statistics"""
        return self.extraction_stats.copy()

    def reset_extraction_statistics(self):
        """Reset extraction statistics"""
        self.extraction_stats = {
            'total_extracted': 0,
            'successful_extractions': 0,
            'failed_extractions': 0,
            'premium_properties': 0,
            'standard_properties': 0
        }

