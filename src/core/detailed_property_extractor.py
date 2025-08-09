#!/usr/bin/env python3
"""
Detailed Property Page Extractor
Extracts comprehensive property information from individual property pages including amenities, 
floor plans, neighborhood data, and detailed specifications.
"""

import time
import json
import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from urllib.parse import urljoin

# Selenium imports
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

# BeautifulSoup for parsing
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


class DetailedPropertyModel:
    """
    Extended property model for detailed property information
    """
    
    def __init__(self):
        """Initialize detailed property model"""
        # Basic property info (from listing page)
        self.basic_info = PropertyModel()
        
        # Detailed amenities
        self.amenities = {
            'indoor': [],
            'outdoor': [],
            'security': [],
            'lifestyle': [],
            'connectivity': []
        }
        
        # Floor plan details
        self.floor_plan = {
            'layout_type': None,
            'room_details': {},
            'dimensions': {},
            'floor_plan_images': []
        }
        
        # Neighborhood information
        self.neighborhood = {
            'schools': [],
            'hospitals': [],
            'shopping_centers': [],
            'restaurants': [],
            'banks': [],
            'metro_stations': [],
            'bus_stops': []
        }
        
        # Detailed pricing
        self.pricing_details = {
            'base_price': None,
            'registration_charges': None,
            'stamp_duty': None,
            'maintenance_charges': None,
            'parking_charges': None,
            'club_membership': None,
            'total_cost': None,
            'price_per_sqft_breakdown': {}
        }
        
        # Builder and project details
        self.project_info = {
            'builder_name': None,
            'project_name': None,
            'rera_id': None,
            'possession_date': None,
            'project_status': None,
            'total_units': None,
            'project_area': None,
            'launch_date': None
        }
        
        # Property specifications
        self.specifications = {
            'flooring': None,
            'walls': None,
            'kitchen': None,
            'bathroom': None,
            'doors_windows': None,
            'electrical': None,
            'plumbing': None,
            'safety_features': []
        }
        
        # Location details
        self.location_details = {
            'latitude': None,
            'longitude': None,
            'address': None,
            'landmark': None,
            'pin_code': None,
            'connectivity_details': {}
        }
        
        # Additional information
        self.additional_info = {
            'property_age': None,
            'ownership_type': None,
            'approved_by': [],
            'water_supply': None,
            'power_backup': None,
            'internet_connectivity': None
        }
        
        # Extraction metadata
        self.extraction_metadata = {
            'extracted_at': datetime.now().isoformat(),
            'source_url': None,
            'extraction_success': False,
            'fields_extracted': 0,
            'total_fields': 0,
            'extraction_errors': []
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        return {
            'basic_info': self.basic_info.__dict__,
            'amenities': self.amenities,
            'floor_plan': self.floor_plan,
            'neighborhood': self.neighborhood,
            'pricing_details': self.pricing_details,
            'project_info': self.project_info,
            'specifications': self.specifications,
            'location_details': self.location_details,
            'additional_info': self.additional_info,
            'extraction_metadata': self.extraction_metadata
        }
    
    def calculate_completeness(self) -> float:
        """Calculate data completeness percentage"""
        total_fields = 0
        filled_fields = 0
        
        # Count all possible fields
        for section in [self.amenities, self.floor_plan, self.neighborhood, 
                       self.pricing_details, self.project_info, self.specifications,
                       self.location_details, self.additional_info]:
            for key, value in section.items():
                total_fields += 1
                if value and (isinstance(value, list) and len(value) > 0 or 
                             isinstance(value, dict) and len(value) > 0 or
                             isinstance(value, str) and value.strip()):
                    filled_fields += 1
        
        self.extraction_metadata['total_fields'] = total_fields
        self.extraction_metadata['fields_extracted'] = filled_fields
        
        return (filled_fields / total_fields) * 100 if total_fields > 0 else 0


class DetailedPropertyExtractor:
    """
    Extracts detailed property information from individual property pages
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize detailed property extractor"""
        self.config = config
        self.logger = ScraperLogger(config)
        
        # Load detailed extraction selectors
        self.selectors = self._load_detailed_selectors()
        
        # Extraction statistics
        self.extraction_stats = {
            'pages_processed': 0,
            'successful_extractions': 0,
            'failed_extractions': 0,
            'avg_completeness': 0.0,
            'total_amenities_extracted': 0,
            'total_neighborhood_items': 0
        }
    
    def _load_detailed_selectors(self) -> Dict[str, Any]:
        """Load selectors for detailed property page extraction"""
        
        # Get Phase II selectors from config or use defaults
        phase2_config = self.config.get('phase2', {})
        return phase2_config.get('selectors', {
            'amenities': {
                'container': '.amenities-section, .features-section, .amenities-list',
                'items': '.amenity-item, .feature-item, li',
                'categories': {
                    'indoor': ['gym', 'swimming pool', 'clubhouse', 'indoor games'],
                    'outdoor': ['garden', 'playground', 'jogging track', 'outdoor sports'],
                    'security': ['security', 'cctv', 'intercom', 'gated community'],
                    'lifestyle': ['spa', 'salon', 'restaurant', 'shopping'],
                    'connectivity': ['wifi', 'broadband', 'cable tv']
                }
            },
            'floor_plan': {
                'container': '.floor-plan-section, .layout-section',
                'layout_type': '.layout-type, .floor-plan-type',
                'room_details': '.room-details, .floor-plan-details',
                'images': '.floor-plan-image img, .layout-image img'
            },
            'neighborhood': {
                'container': '.nearby-section, .locality-section, .neighborhood',
                'schools': '.schools-section, .education-section',
                'hospitals': '.hospitals-section, .medical-section',
                'shopping': '.shopping-section, .retail-section',
                'transport': '.transport-section, .connectivity-section'
            },
            'pricing': {
                'container': '.pricing-section, .cost-breakdown',
                'base_price': '.base-price, .property-price',
                'additional_charges': '.additional-charges, .other-charges',
                'breakdown': '.price-breakdown, .cost-details'
            },
            'project_info': {
                'container': '.project-section, .builder-section',
                'builder': '.builder-name, .developer-name',
                'project': '.project-name, .society-name',
                'rera': '.rera-id, .rera-number',
                'possession': '.possession-date, .ready-date'
            },
            'specifications': {
                'container': '.specifications-section, .features-section',
                'flooring': '.flooring, .floor-type',
                'kitchen': '.kitchen-details, .kitchen-specs',
                'bathroom': '.bathroom-details, .bathroom-specs'
            },
            'location': {
                'container': '.location-section, .address-section',
                'address': '.full-address, .property-address',
                'coordinates': '.coordinates, .map-data',
                'connectivity': '.connectivity-details, .transport-details'
            }
        })
    
    def extract_detailed_property(self, driver: webdriver.Chrome, url: str, 
                                 basic_metadata: Optional[Dict[str, Any]] = None) -> DetailedPropertyModel:
        """
        Extract detailed property information from property page
        
        Args:
            driver: Selenium WebDriver instance
            url: Property page URL
            basic_metadata: Basic property info from listing page
        """
        
        detailed_property = DetailedPropertyModel()
        detailed_property.extraction_metadata['source_url'] = url
        
        try:
            # Navigate to property page
            driver.get(url)
            
            # Wait for page load with dynamic content
            self._wait_for_page_load(driver)
            
            # Get page source
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            
            # Extract different sections
            self._extract_amenities(soup, detailed_property)
            self._extract_floor_plan(soup, detailed_property)
            self._extract_neighborhood(soup, detailed_property)
            self._extract_pricing_details(soup, detailed_property)
            self._extract_project_info(soup, detailed_property)
            self._extract_specifications(soup, detailed_property)
            self._extract_location_details(soup, detailed_property)
            self._extract_additional_info(soup, detailed_property)
            
            # Calculate completeness
            completeness = detailed_property.calculate_completeness()
            
            # Update extraction metadata
            detailed_property.extraction_metadata['extraction_success'] = completeness > 30  # 30% threshold
            
            # Update statistics
            self.extraction_stats['pages_processed'] += 1
            if detailed_property.extraction_metadata['extraction_success']:
                self.extraction_stats['successful_extractions'] += 1
            else:
                self.extraction_stats['failed_extractions'] += 1
            
            # Update average completeness
            current_avg = self.extraction_stats['avg_completeness']
            pages_count = self.extraction_stats['pages_processed']
            self.extraction_stats['avg_completeness'] = ((current_avg * (pages_count - 1)) + completeness) / pages_count
            
            self.logger.logger.info(f"✅ Extracted detailed property data: {completeness:.1f}% complete")
            
            return detailed_property
            
        except Exception as e:
            detailed_property.extraction_metadata['extraction_errors'].append(str(e))
            self.logger.log_error("DETAILED_EXTRACTION", f"Failed to extract from {url}: {str(e)}")
            
            self.extraction_stats['pages_processed'] += 1
            self.extraction_stats['failed_extractions'] += 1
            
            return detailed_property
    
    def _wait_for_page_load(self, driver: webdriver.Chrome, timeout: int = 15):
        """Wait for page to load with dynamic content"""
        try:
            # Wait for basic page structure
            WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Additional wait for dynamic content
            time.sleep(3)
            
            # Try to wait for specific content sections
            try:
                WebDriverWait(driver, 5).until(
                    EC.any_of(
                        EC.presence_of_element_located((By.CLASS_NAME, "amenities")),
                        EC.presence_of_element_located((By.CLASS_NAME, "features")),
                        EC.presence_of_element_located((By.CLASS_NAME, "specifications"))
                    )
                )
            except TimeoutException:
                # Continue if specific sections not found
                pass
                
        except TimeoutException:
            self.logger.log_error("PAGE_LOAD", f"Page load timeout for {driver.current_url}")
    
    def _extract_amenities(self, soup: BeautifulSoup, property_model: DetailedPropertyModel):
        """Extract amenities and categorize them"""
        try:
            amenities_section = soup.select_one(self.selectors['amenities']['container'])
            if not amenities_section:
                return
            
            # Get all amenity items
            amenity_items = amenities_section.select(self.selectors['amenities']['items'])
            
            total_amenities = 0
            for item in amenity_items:
                amenity_text = item.get_text(strip=True).lower()
                if len(amenity_text) < 3:  # Skip very short text
                    continue
                
                # Categorize amenity
                categorized = False
                for category, keywords in self.selectors['amenities']['categories'].items():
                    if any(keyword in amenity_text for keyword in keywords):
                        property_model.amenities[category].append(amenity_text.title())
                        categorized = True
                        total_amenities += 1
                        break
                
                # If not categorized, add to lifestyle
                if not categorized and len(amenity_text) > 5:
                    property_model.amenities['lifestyle'].append(amenity_text.title())
                    total_amenities += 1
            
            self.extraction_stats['total_amenities_extracted'] += total_amenities
            
        except Exception as e:
            property_model.extraction_metadata['extraction_errors'].append(f"Amenities extraction: {str(e)}")
    
    def _extract_floor_plan(self, soup: BeautifulSoup, property_model: DetailedPropertyModel):
        """Extract floor plan information"""
        try:
            floor_plan_section = soup.select_one(self.selectors['floor_plan']['container'])
            if not floor_plan_section:
                return
            
            # Extract layout type
            layout_elem = floor_plan_section.select_one(self.selectors['floor_plan']['layout_type'])
            if layout_elem:
                property_model.floor_plan['layout_type'] = layout_elem.get_text(strip=True)
            
            # Extract room details
            room_details_elem = floor_plan_section.select_one(self.selectors['floor_plan']['room_details'])
            if room_details_elem:
                room_text = room_details_elem.get_text(strip=True)
                property_model.floor_plan['room_details']['description'] = room_text
            
            # Extract floor plan images
            image_elements = floor_plan_section.select(self.selectors['floor_plan']['images'])
            for img in image_elements:
                img_src = img.get('src') or img.get('data-src')
                if img_src:
                    property_model.floor_plan['floor_plan_images'].append(img_src)
            
        except Exception as e:
            property_model.extraction_metadata['extraction_errors'].append(f"Floor plan extraction: {str(e)}")
    
    def _extract_neighborhood(self, soup: BeautifulSoup, property_model: DetailedPropertyModel):
        """Extract neighborhood information"""
        try:
            neighborhood_section = soup.select_one(self.selectors['neighborhood']['container'])
            if not neighborhood_section:
                return
            
            # Extract schools
            schools_section = neighborhood_section.select_one(self.selectors['neighborhood']['schools'])
            if schools_section:
                schools = self._extract_nearby_items(schools_section)
                property_model.neighborhood['schools'] = schools
                self.extraction_stats['total_neighborhood_items'] += len(schools)
            
            # Extract hospitals
            hospitals_section = neighborhood_section.select_one(self.selectors['neighborhood']['hospitals'])
            if hospitals_section:
                hospitals = self._extract_nearby_items(hospitals_section)
                property_model.neighborhood['hospitals'] = hospitals
                self.extraction_stats['total_neighborhood_items'] += len(hospitals)
            
            # Extract shopping centers
            shopping_section = neighborhood_section.select_one(self.selectors['neighborhood']['shopping'])
            if shopping_section:
                shopping = self._extract_nearby_items(shopping_section)
                property_model.neighborhood['shopping_centers'] = shopping
                self.extraction_stats['total_neighborhood_items'] += len(shopping)
            
            # Extract transport connectivity
            transport_section = neighborhood_section.select_one(self.selectors['neighborhood']['transport'])
            if transport_section:
                transport = self._extract_nearby_items(transport_section)
                property_model.neighborhood['metro_stations'] = transport
                self.extraction_stats['total_neighborhood_items'] += len(transport)
            
        except Exception as e:
            property_model.extraction_metadata['extraction_errors'].append(f"Neighborhood extraction: {str(e)}")
    
    def _extract_nearby_items(self, section: BeautifulSoup) -> List[str]:
        """Extract nearby items from a section"""
        items = []
        
        # Try different selectors for items
        item_selectors = ['li', '.item', '.nearby-item', 'div', 'span']
        
        for selector in item_selectors:
            elements = section.select(selector)
            for elem in elements:
                text = elem.get_text(strip=True)
                if len(text) > 3 and text not in items:
                    items.append(text)
            
            if items:  # If we found items with this selector, stop trying others
                break
        
        return items[:10]  # Limit to 10 items per category
    
    def _extract_pricing_details(self, soup: BeautifulSoup, property_model: DetailedPropertyModel):
        """Extract detailed pricing information"""
        try:
            pricing_section = soup.select_one(self.selectors['pricing']['container'])
            if not pricing_section:
                return
            
            # Extract base price
            base_price_elem = pricing_section.select_one(self.selectors['pricing']['base_price'])
            if base_price_elem:
                property_model.pricing_details['base_price'] = base_price_elem.get_text(strip=True)
            
            # Extract additional charges
            charges_section = pricing_section.select_one(self.selectors['pricing']['additional_charges'])
            if charges_section:
                charges_text = charges_section.get_text()
                
                # Parse different types of charges
                if 'registration' in charges_text.lower():
                    reg_match = re.search(r'registration[:\s]*₹?([0-9,]+)', charges_text, re.IGNORECASE)
                    if reg_match:
                        property_model.pricing_details['registration_charges'] = f"₹{reg_match.group(1)}"
                
                if 'maintenance' in charges_text.lower():
                    maint_match = re.search(r'maintenance[:\s]*₹?([0-9,]+)', charges_text, re.IGNORECASE)
                    if maint_match:
                        property_model.pricing_details['maintenance_charges'] = f"₹{maint_match.group(1)}"
            
        except Exception as e:
            property_model.extraction_metadata['extraction_errors'].append(f"Pricing extraction: {str(e)}")
    
    def _extract_project_info(self, soup: BeautifulSoup, property_model: DetailedPropertyModel):
        """Extract project and builder information"""
        try:
            project_section = soup.select_one(self.selectors['project_info']['container'])
            if not project_section:
                return
            
            # Extract builder name
            builder_elem = project_section.select_one(self.selectors['project_info']['builder'])
            if builder_elem:
                property_model.project_info['builder_name'] = builder_elem.get_text(strip=True)
            
            # Extract project name
            project_elem = project_section.select_one(self.selectors['project_info']['project'])
            if project_elem:
                property_model.project_info['project_name'] = project_elem.get_text(strip=True)
            
            # Extract RERA ID
            rera_elem = project_section.select_one(self.selectors['project_info']['rera'])
            if rera_elem:
                property_model.project_info['rera_id'] = rera_elem.get_text(strip=True)
            
            # Extract possession date
            possession_elem = project_section.select_one(self.selectors['project_info']['possession'])
            if possession_elem:
                property_model.project_info['possession_date'] = possession_elem.get_text(strip=True)
            
        except Exception as e:
            property_model.extraction_metadata['extraction_errors'].append(f"Project info extraction: {str(e)}")
    
    def _extract_specifications(self, soup: BeautifulSoup, property_model: DetailedPropertyModel):
        """Extract property specifications"""
        try:
            specs_section = soup.select_one(self.selectors['specifications']['container'])
            if not specs_section:
                return
            
            # Extract flooring details
            flooring_elem = specs_section.select_one(self.selectors['specifications']['flooring'])
            if flooring_elem:
                property_model.specifications['flooring'] = flooring_elem.get_text(strip=True)
            
            # Extract kitchen details
            kitchen_elem = specs_section.select_one(self.selectors['specifications']['kitchen'])
            if kitchen_elem:
                property_model.specifications['kitchen'] = kitchen_elem.get_text(strip=True)
            
            # Extract bathroom details
            bathroom_elem = specs_section.select_one(self.selectors['specifications']['bathroom'])
            if bathroom_elem:
                property_model.specifications['bathroom'] = bathroom_elem.get_text(strip=True)
            
        except Exception as e:
            property_model.extraction_metadata['extraction_errors'].append(f"Specifications extraction: {str(e)}")
    
    def _extract_location_details(self, soup: BeautifulSoup, property_model: DetailedPropertyModel):
        """Extract detailed location information"""
        try:
            location_section = soup.select_one(self.selectors['location']['container'])
            if not location_section:
                return
            
            # Extract full address
            address_elem = location_section.select_one(self.selectors['location']['address'])
            if address_elem:
                property_model.location_details['address'] = address_elem.get_text(strip=True)
            
            # Try to extract coordinates from map data or scripts
            coord_elem = location_section.select_one(self.selectors['location']['coordinates'])
            if coord_elem:
                coord_text = coord_elem.get_text()
                lat_match = re.search(r'lat[:\s]*([0-9.-]+)', coord_text)
                lng_match = re.search(r'lng[:\s]*([0-9.-]+)', coord_text)
                
                if lat_match and lng_match:
                    property_model.location_details['latitude'] = lat_match.group(1)
                    property_model.location_details['longitude'] = lng_match.group(1)
            
        except Exception as e:
            property_model.extraction_metadata['extraction_errors'].append(f"Location extraction: {str(e)}")
    
    def _extract_additional_info(self, soup: BeautifulSoup, property_model: DetailedPropertyModel):
        """Extract additional property information"""
        try:
            # Extract property age
            age_pattern = r'(\d+)\s*year[s]?\s*old'
            age_match = re.search(age_pattern, soup.get_text(), re.IGNORECASE)
            if age_match:
                property_model.additional_info['property_age'] = f"{age_match.group(1)} years"
            
            # Extract ownership type
            ownership_keywords = ['freehold', 'leasehold', 'co-operative']
            text_content = soup.get_text().lower()
            for keyword in ownership_keywords:
                if keyword in text_content:
                    property_model.additional_info['ownership_type'] = keyword.title()
                    break
            
            # Extract approvals
            approval_keywords = ['rera approved', 'municipal approved', 'bank approved']
            approvals = []
            for keyword in approval_keywords:
                if keyword in text_content:
                    approvals.append(keyword.title())
            
            if approvals:
                property_model.additional_info['approved_by'] = approvals
            
        except Exception as e:
            property_model.extraction_metadata['extraction_errors'].append(f"Additional info extraction: {str(e)}")
    
    def get_extraction_statistics(self) -> Dict[str, Any]:
        """Get detailed extraction statistics"""
        return {
            'extraction_stats': self.extraction_stats,
            'success_rate': (self.extraction_stats['successful_extractions'] / 
                           max(1, self.extraction_stats['pages_processed'])) * 100,
            'avg_completeness': self.extraction_stats['avg_completeness']
        }


# Export for easy import
__all__ = ['DetailedPropertyExtractor', 'DetailedPropertyModel']
