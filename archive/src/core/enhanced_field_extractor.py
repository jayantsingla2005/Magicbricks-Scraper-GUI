#!/usr/bin/env python3
"""
Enhanced Field Extractor with Targeted Fixes
Implements specific fixes based on comprehensive research findings for area field mapping and society field extraction.
"""

import re
import json
from typing import Dict, List, Any, Optional, Tuple
from bs4 import BeautifulSoup

try:
    from ..models.property_model import PropertyModel
    from ..utils.logger import ScraperLogger
except ImportError:
    # Fallback for direct execution
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).parent.parent))
    from models.property_model import PropertyModel
    from utils.logger import ScraperLogger


class EnhancedFieldExtractor:
    """
    Enhanced field extractor with targeted fixes for area mapping and society extraction
    Based on comprehensive research findings across property types
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize enhanced field extractor"""
        self.config = config
        self.extraction_stats = {
            'area_extractions': {'super': 0, 'carpet': 0, 'plot': 0, 'fallback': 0},
            'society_extractions': {'link': 0, 'text': 0, 'fallback': 0},
            'unit_conversions': {'sqft': 0, 'sqyrd': 0, 'acres': 0},
            'property_type_detections': {'apartment': 0, 'house': 0, 'plot': 0, 'other': 0}
        }
    
    def extract_enhanced_property_data(self, soup: BeautifulSoup, position: int) -> PropertyModel:
        """Extract property data with enhanced field extraction"""
        property_data = PropertyModel()
        all_text = soup.get_text()
        
        # Step 1: Enhanced property type detection
        property_type = self._detect_property_type_enhanced(soup, all_text)
        
        # Step 2: Enhanced area extraction with targeted fixes
        self._extract_area_enhanced(soup, all_text, property_data, property_type)
        
        # Step 3: Enhanced society extraction with multiple fallbacks
        self._extract_society_enhanced(soup, all_text, property_data, property_type)
        
        # Step 4: Enhanced status extraction with conditional logic
        self._extract_status_enhanced(soup, all_text, property_data, property_type)
        
        # Step 5: Standard field extraction with improvements
        self._extract_standard_fields_enhanced(soup, all_text, property_data)
        
        # Step 6: Data normalization and validation
        self._normalize_and_validate_data(property_data)
        
        return property_data
    
    def _detect_property_type_enhanced(self, soup: BeautifulSoup, all_text: str) -> str:
        """Enhanced property type detection with better accuracy"""
        
        # Get title for analysis
        title_elem = soup.select_one('h2, .mb-srp__card__title, [class*="title"]')
        title = title_elem.get_text(strip=True).lower() if title_elem else ""
        
        # Combined text for analysis
        combined_text = (title + " " + all_text[:500]).lower()
        
        # Enhanced property type patterns
        property_patterns = {
            'plot': [
                r'\bplot\b', r'\bland\b', r'\bresidential plot\b', r'\bplotted\b',
                r'\bplot area\b', r'\bland area\b', r'\bplot for sale\b'
            ],
            'house': [
                r'\bindependent house\b', r'\bhouse\b', r'\bvilla\b', r'\bkothi\b',
                r'\bindependent\b.*\bhouse\b', r'\brow house\b', r'\btownhouse\b'
            ],
            'floor': [
                r'\bindependent floor\b', r'\bbuilder floor\b', r'\bfloor\b.*\bsale\b',
                r'\bmulti.*floor\b', r'\bground floor\b', r'\bfirst floor\b'
            ],
            'apartment': [
                r'\bapartment\b', r'\bflat\b', r'\bbhk\b', r'\bunit\b',
                r'\bresidential.*apartment\b', r'\bservice.*apartment\b'
            ]
        }
        
        # Score each property type
        type_scores = {}
        for prop_type, patterns in property_patterns.items():
            score = 0
            for pattern in patterns:
                matches = len(re.findall(pattern, combined_text))
                score += matches
            type_scores[prop_type] = score
        
        # Determine property type
        if type_scores['plot'] > 0:
            detected_type = 'plot'
        elif type_scores['house'] > 0:
            detected_type = 'house'
        elif type_scores['floor'] > 0:
            detected_type = 'floor'
        else:
            detected_type = 'apartment'  # Default

        # Update statistics
        if detected_type in self.extraction_stats['property_type_detections']:
            self.extraction_stats['property_type_detections'][detected_type] += 1
        else:
            self.extraction_stats['property_type_detections']['other'] += 1
        
        return detected_type
    
    def _extract_area_enhanced(self, soup: BeautifulSoup, all_text: str, 
                              property_data: PropertyModel, property_type: str):
        """Enhanced area extraction with targeted fixes"""
        
        # Enhanced area patterns with better comma and space handling
        area_patterns = {
            'super_area': [
                r'Super Area[:\s]*(\d+(?:,\d+)*(?:\.\d+)?)\s*(sqft|sq\.?\s*ft|sqyrd|sq\.?\s*yard|acres?)',
                r'Built[- ]?up Area[:\s]*(\d+(?:,\d+)*(?:\.\d+)?)\s*(sqft|sq\.?\s*ft|sqyrd|sq\.?\s*yard)',
                r'Total Area[:\s]*(\d+(?:,\d+)*(?:\.\d+)?)\s*(sqft|sq\.?\s*ft|sqyrd|sq\.?\s*yard)'
            ],
            'carpet_area': [
                r'Carpet Area[:\s]*(\d+(?:,\d+)*(?:\.\d+)?)\s*(sqft|sq\.?\s*ft|sqyrd|sq\.?\s*yard)',
                r'Usable Area[:\s]*(\d+(?:,\d+)*(?:\.\d+)?)\s*(sqft|sq\.?\s*ft|sqyrd|sq\.?\s*yard)',
                r'Net Area[:\s]*(\d+(?:,\d+)*(?:\.\d+)?)\s*(sqft|sq\.?\s*ft|sqyrd|sq\.?\s*yard)',
                r'Built[- ]?up Area[:\s]*(\d+(?:,\d+)*(?:\.\d+)?)\s*(sqft|sq\.?\s*ft|sqyrd|sq\.?\s*yard)'
            ],
            'plot_area': [
                r'Plot Area[:\s]*(\d+(?:,\d+)*(?:\.\d+)?)\s*(sqft|sq\.?\s*ft|sqyrd|sq\.?\s*yard|acres?)',
                r'Land Area[:\s]*(\d+(?:,\d+)*(?:\.\d+)?)\s*(sqft|sq\.?\s*ft|sqyrd|sq\.?\s*yard|acres?)',
                r'Site Area[:\s]*(\d+(?:,\d+)*(?:\.\d+)?)\s*(sqft|sq\.?\s*ft|sqyrd|sq\.?\s*yard|acres?)'
            ]
        }
        
        # Property-type-specific extraction priority
        if property_type == 'plot':
            extraction_order = ['plot_area', 'super_area', 'carpet_area']
        elif property_type == 'house':
            extraction_order = ['carpet_area', 'super_area', 'plot_area']
        else:  # apartment, floor
            extraction_order = ['super_area', 'carpet_area', 'plot_area']
        
        # Extract area with priority order - extract all available areas
        areas_found = {}

        for area_type in area_patterns:
            for pattern in area_patterns[area_type]:
                match = re.search(pattern, all_text, re.IGNORECASE)
                if match:
                    area_value = match.group(1)
                    area_unit = match.group(2).lower()

                    # Normalize area value and unit
                    normalized_area = self._normalize_area_value(area_value, area_unit)
                    areas_found[area_type] = normalized_area
                    break  # Found area for this type, move to next type

        # Assign areas based on property type and availability
        if property_type == 'plot':
            if 'plot_area' in areas_found:
                property_data.super_area = areas_found['plot_area']
                self.extraction_stats['area_extractions']['plot'] += 1
            elif 'super_area' in areas_found:
                property_data.super_area = areas_found['super_area']
                self.extraction_stats['area_extractions']['super'] += 1
        elif property_type == 'house':
            # For houses, prefer plot_area as super_area and carpet_area separately
            if 'plot_area' in areas_found:
                property_data.super_area = areas_found['plot_area']
                self.extraction_stats['area_extractions']['plot'] += 1
            elif 'super_area' in areas_found:
                property_data.super_area = areas_found['super_area']
                self.extraction_stats['area_extractions']['super'] += 1

            if 'carpet_area' in areas_found:
                property_data.carpet_area = areas_found['carpet_area']
                self.extraction_stats['area_extractions']['carpet'] += 1
        else:
            # For apartments, floors
            if 'super_area' in areas_found:
                property_data.super_area = areas_found['super_area']
                self.extraction_stats['area_extractions']['super'] += 1
            if 'carpet_area' in areas_found:
                property_data.carpet_area = areas_found['carpet_area']
                self.extraction_stats['area_extractions']['carpet'] += 1

        # If no specific areas found, try fallback
        if not property_data.super_area and not property_data.carpet_area:
            # Fallback: General area pattern
            fallback_patterns = [
                r'(\d+(?:,\d+)*(?:\.\d+)?)\s*(sqft|sq\.?\s*ft|sqyrd|sq\.?\s*yard|acres?)',
                r'Area[:\s]*(\d+(?:,\d+)*(?:\.\d+)?)\s*(sqft|sq\.?\s*ft|sqyrd|sq\.?\s*yard)'
            ]

            for pattern in fallback_patterns:
                match = re.search(pattern, all_text, re.IGNORECASE)
                if match:
                    area_value = match.group(1)
                    area_unit = match.group(2).lower()
                    normalized_area = self._normalize_area_value(area_value, area_unit)

                    # Assign based on property type preference
                    if property_type in ['house', 'floor']:
                        property_data.carpet_area = normalized_area
                    else:
                        property_data.super_area = normalized_area

                    self.extraction_stats['area_extractions']['fallback'] += 1
                    break
    
    def _normalize_area_value(self, area_value: str, area_unit: str) -> str:
        """Normalize area value and unit"""
        
        # Clean area value (remove commas)
        clean_value = area_value.replace(',', '')
        
        # Convert to float for unit conversion
        try:
            numeric_value = float(clean_value)
        except ValueError:
            return f"{area_value} {area_unit}"  # Return original if conversion fails
        
        # Unit conversion and normalization
        if 'sqyrd' in area_unit or 'yard' in area_unit:
            # Convert square yards to square feet (1 sqyrd = 9 sqft)
            converted_value = numeric_value * 9
            normalized_unit = 'sqft'
            self.extraction_stats['unit_conversions']['sqyrd'] += 1
        elif 'acres' in area_unit:
            # Convert acres to square feet (1 acre = 43,560 sqft)
            converted_value = numeric_value * 43560
            normalized_unit = 'sqft'
            self.extraction_stats['unit_conversions']['acres'] += 1
        else:
            # Keep sqft as is
            converted_value = numeric_value
            normalized_unit = 'sqft'
            self.extraction_stats['unit_conversions']['sqft'] += 1
        
        # Format the result
        if converted_value >= 1000:
            # Add comma for thousands
            formatted_value = f"{converted_value:,.0f}"
        else:
            formatted_value = f"{converted_value:.0f}"
        
        return f"{formatted_value} {normalized_unit}"
    
    def _extract_society_enhanced(self, soup: BeautifulSoup, all_text: str, 
                                 property_data: PropertyModel, property_type: str):
        """Enhanced society extraction with multiple fallback strategies"""
        
        # Strategy 1: Link-based extraction (most reliable)
        society_link_selectors = [
            'a[href*="pdpid"]',
            'a[href*="society"]',
            'a[href*="project"]',
            '[class*="society"] a',
            '[class*="project"] a'
        ]
        
        for selector in society_link_selectors:
            society_elements = soup.select(selector)
            for elem in society_elements:
                society_text = elem.get_text(strip=True)
                if society_text and len(society_text) > 3:  # Valid society name
                    property_data.society = society_text
                    self.extraction_stats['society_extractions']['link'] += 1
                    return
        
        # Strategy 2: Text-based extraction with patterns
        society_patterns = [
            r'Society[:\s]*([A-Za-z0-9\s,.-]+?)(?:\n|,|\||$)',
            r'Project[:\s]*([A-Za-z0-9\s,.-]+?)(?:\n|,|\||$)',
            r'Complex[:\s]*([A-Za-z0-9\s,.-]+?)(?:\n|,|\||$)',
            r'in\s+([A-Za-z0-9\s,.-]+?)\s+(?:Society|Complex|Project)',
            r'([A-Za-z0-9\s,.-]+?)\s+(?:Society|Complex|Project|Apartments|Residency)'
        ]
        
        for pattern in society_patterns:
            match = re.search(pattern, all_text, re.IGNORECASE)
            if match:
                society_name = match.group(1).strip()
                # Validate society name
                if self._is_valid_society_name(society_name):
                    property_data.society = society_name
                    self.extraction_stats['society_extractions']['text'] += 1
                    return
        
        # Strategy 3: Property-type-specific handling
        if property_type in ['house', 'plot']:
            # For independent houses and plots, society might not exist
            # Look for locality or area name instead
            locality_patterns = [
                r'in\s+(Sector\s+\d+|[A-Za-z0-9\s]{3,20})(?:\s+for\s+sale|\s*,|\s*\||\s*$)',
                r'Located\s+in\s+([A-Za-z0-9\s]{3,20})(?:\s*,|\s*\||\s*$)',
                r'(Sector\s+\d+|[A-Za-z0-9\s]{3,20})\s+(?:Locality|Area|Block)'
            ]
            
            for pattern in locality_patterns:
                match = re.search(pattern, all_text, re.IGNORECASE)
                if match:
                    locality_name = match.group(1).strip()
                    if self._is_valid_society_name(locality_name):
                        # Clean up the locality name
                        clean_locality = locality_name.replace('for Sale', '').replace('for sale', '').strip()
                        property_data.society = f"Near {clean_locality}"
                        self.extraction_stats['society_extractions']['fallback'] += 1
                        return
        
        # Strategy 4: Fallback - extract from title or description
        title_elem = soup.select_one('h2, .mb-srp__card__title, [class*="title"]')
        if title_elem:
            title_text = title_elem.get_text(strip=True)
            # Look for society/project name in title
            title_patterns = [
                r'in\s+([A-Za-z0-9\s,.-]+?)(?:\s+for\s+sale|\s*,|\s*$)',
                r'([A-Za-z0-9\s,.-]+?)\s+(?:Society|Complex|Project|Apartments|Residency)'
            ]
            
            for pattern in title_patterns:
                match = re.search(pattern, title_text, re.IGNORECASE)
                if match:
                    society_name = match.group(1).strip()
                    if self._is_valid_society_name(society_name):
                        property_data.society = society_name
                        self.extraction_stats['society_extractions']['fallback'] += 1
                        return
    
    def _is_valid_society_name(self, name: str) -> bool:
        """Validate if extracted text is a valid society name"""
        if not name or len(name.strip()) < 3:
            return False
        
        # Remove common invalid patterns
        invalid_patterns = [
            r'^\d+$',  # Only numbers
            r'^(for|sale|rent|buy|property|bhk|sqft|cr|lac)$',  # Common property terms
            r'^(the|and|or|in|at|on|by)$',  # Common articles/prepositions
            r'^\W+$'  # Only special characters
        ]
        
        for pattern in invalid_patterns:
            if re.match(pattern, name.strip(), re.IGNORECASE):
                return False
        
        return True
    
    def _extract_status_enhanced(self, soup: BeautifulSoup, all_text: str, 
                                property_data: PropertyModel, property_type: str):
        """Enhanced status extraction with property-type-specific logic"""
        
        # Standard status patterns
        status_patterns = [
            r'(Ready to Move)',
            r'(Under Construction)',
            r'(New Launch)',
            r'(New Property)',
            r'(Resale)',
            r'Possession by ([A-Za-z]+ \'\d+)',
            r'Poss\. by ([A-Za-z]+ \'\d+)',
            r'(Immediate Possession)',
            r'(Available)'
        ]
        
        # Try standard patterns first
        for pattern in status_patterns:
            match = re.search(pattern, all_text, re.IGNORECASE)
            if match:
                property_data.status = match.group(1) if match.groups() else match.group(0)
                return
        
        # Property-type-specific status handling
        if property_type == 'plot':
            # Plots use different status terminology
            plot_patterns = [
                r'Transaction[:\s]*(\w+)',
                r'Type[:\s]*(\w+)',
                r'(Resale Plot)',
                r'(New Plot)',
                r'(Available for Sale)'
            ]
            
            for pattern in plot_patterns:
                match = re.search(pattern, all_text, re.IGNORECASE)
                if match:
                    status = match.group(1) if match.groups() else match.group(0)
                    # Map plot-specific status
                    if status.lower() == 'resale':
                        property_data.status = 'Resale Plot'
                    elif status.lower() == 'new':
                        property_data.status = 'New Plot'
                    else:
                        property_data.status = status
                    return
            
            # Default for plots
            property_data.status = 'Available'
    
    def _extract_standard_fields_enhanced(self, soup: BeautifulSoup, all_text: str, 
                                         property_data: PropertyModel):
        """Extract standard fields with enhanced patterns"""
        
        # Enhanced title extraction
        title_selectors = ['h2', '.mb-srp__card__title', '[class*="title"]', 'h1', 'h3']
        for selector in title_selectors:
            title_elem = soup.select_one(selector)
            if title_elem:
                property_data.title = title_elem.get_text(strip=True)
                break
        
        # Enhanced price extraction with better patterns
        price_patterns = [
            r'₹\s*(\d+(?:\.\d+)?)\s*(Cr|Crore)',
            r'₹\s*(\d+(?:\.\d+)?)\s*(Lac|Lakh)',
            r'₹\s*(\d+(?:,\d+)*(?:\.\d+)?)\s*(Cr|Crore|Lac|Lakh)',
            r'Price[:\s]*₹\s*(\d+(?:,\d+)*(?:\.\d+)?)\s*(Cr|Crore|Lac|Lakh)'
        ]
        
        for pattern in price_patterns:
            match = re.search(pattern, all_text, re.IGNORECASE)
            if match:
                amount = match.group(1)
                unit = match.group(2)
                property_data.price = f"₹{amount} {unit}"
                break
        
        # Enhanced bedroom extraction
        bedroom_patterns = [
            r'(\d+)\s*BHK',
            r'(\d+)\s*Bedroom',
            r'(\d+)\s*BR',
            r'Bedrooms?[:\s]*(\d+)'
        ]
        
        for pattern in bedroom_patterns:
            match = re.search(pattern, all_text, re.IGNORECASE)
            if match:
                property_data.bedrooms = match.group(1)
                break
    
    def _normalize_and_validate_data(self, property_data: PropertyModel):
        """Normalize and validate extracted data"""
        
        # Normalize price format
        if property_data.price:
            # Ensure consistent price format
            price_text = property_data.price
            price_text = re.sub(r'₹\s*', '₹', price_text)  # Remove extra spaces after ₹
            price_text = re.sub(r'\s+', ' ', price_text)  # Normalize spaces
            property_data.price = price_text
        
        # Normalize society name
        if property_data.society:
            society_text = property_data.society
            society_text = re.sub(r'\s+', ' ', society_text)  # Normalize spaces
            society_text = society_text.strip()
            property_data.society = society_text
        
        # Validate and clean title
        if property_data.title:
            title_text = property_data.title
            title_text = re.sub(r'\s+', ' ', title_text)  # Normalize spaces
            title_text = title_text.strip()
            property_data.title = title_text
    
    def get_extraction_statistics(self) -> Dict[str, Any]:
        """Get detailed extraction statistics"""
        return {
            'extraction_stats': self.extraction_stats,
            'total_extractions': {
                'area': sum(self.extraction_stats['area_extractions'].values()),
                'society': sum(self.extraction_stats['society_extractions'].values()),
                'unit_conversions': sum(self.extraction_stats['unit_conversions'].values()),
                'property_types': sum(self.extraction_stats['property_type_detections'].values())
            }
        }


# Export for easy import
__all__ = ['EnhancedFieldExtractor']
