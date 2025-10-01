#!/usr/bin/env python3
"""
Data Validator Module
Handles property data validation, cleaning, and filtering.
Extracted from integrated_magicbricks_scraper.py for better maintainability.
"""

import re
import logging
from typing import Dict, List, Any, Optional


class DataValidator:
    """
    Validates, cleans, and filters property data for quality assurance
    """
    
    def __init__(self, config: Dict[str, Any] = None, logger=None):
        """
        Initialize data validator
        
        Args:
            config: Configuration dictionary with filtering criteria
            logger: Logger instance
        """
        self.config = config or {}
        self.logger = logger or logging.getLogger(__name__)
        
        # Filter statistics
        self._filter_stats = {
            'total': 0,
            'filtered': 0,
            'excluded': 0
        }
    
    def validate_and_clean_property_data(self, property_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and clean property data for quality assurance
        
        Args:
            property_data: Raw property data dictionary
            
        Returns:
            Cleaned and validated property data dictionary
        """
        
        cleaned_data = property_data.copy()
        validation_issues = []
        
        try:
            # Clean and validate title
            title = cleaned_data.get('title', '').strip()
            if title:
                # Remove excessive whitespace and normalize
                title = ' '.join(title.split())
                # Remove common unwanted characters
                title = title.replace('\n', ' ').replace('\t', ' ')
                cleaned_data['title'] = title
            else:
                validation_issues.append('Missing title')
            
            # Clean and validate price
            price = cleaned_data.get('price', '').strip()
            if price:
                # Normalize price format
                price = price.replace('₹', '').replace(',', '').strip()
                # Validate price contains numbers
                if not any(char.isdigit() for char in price):
                    validation_issues.append('Invalid price format')
                cleaned_data['price'] = price
            else:
                validation_issues.append('Missing price')
            
            # Clean and validate area
            area = cleaned_data.get('area', '').strip()
            if area:
                # Normalize area format
                area = area.replace(',', '').strip()
                cleaned_data['area'] = area
            else:
                validation_issues.append('Missing area')
            
            # Validate and clean property URL
            url = cleaned_data.get('property_url', '').strip()
            if url:
                if not url.startswith('http'):
                    if url.startswith('/'):
                        cleaned_data['property_url'] = f"https://www.magicbricks.com{url}"
                    else:
                        validation_issues.append('Invalid URL format')
            # NOTE: Missing URLs are normal for builder floors/plots - don't mark as invalid
            
            # Clean locality and society
            for field in ['locality', 'society']:
                value = cleaned_data.get(field, '').strip()
                if value:
                    # Remove excessive whitespace and normalize
                    value = ' '.join(value.split())
                    cleaned_data[field] = value
            
            # Validate numeric fields
            for field in ['bathrooms', 'balcony']:
                value = cleaned_data.get(field, '')
                if value and isinstance(value, str):
                    # Extract numeric value
                    numbers = re.findall(r'\d+', value)
                    if numbers:
                        cleaned_data[field] = numbers[0]
            
            # Clean and validate posting date
            posting_date = cleaned_data.get('posting_date_text', '').strip()
            if posting_date:
                # Normalize date format
                posting_date = ' '.join(posting_date.split())
                cleaned_data['posting_date_text'] = posting_date
            
            # Add data quality score
            total_fields = len([k for k in cleaned_data.keys() if k not in ['scraped_at', 'session_id', 'page_number', 'property_index']])
            filled_fields = len([v for v in cleaned_data.values() if v and str(v).strip()])
            quality_score = (filled_fields / total_fields) * 100 if total_fields > 0 else 0
            
            cleaned_data['data_quality_score'] = round(quality_score, 1)
            cleaned_data['validation_issues'] = validation_issues
            cleaned_data['is_valid'] = len(validation_issues) == 0
            
            return cleaned_data
            
        except Exception as e:
            self.logger.warning(f"Error validating property data: {str(e)}")
            cleaned_data['validation_issues'] = validation_issues + [f"Validation error: {str(e)}"]
            cleaned_data['is_valid'] = False
            return cleaned_data
    
    def apply_property_filters(self, property_data: Dict[str, Any]) -> bool:
        """
        Apply filtering criteria to determine if property should be included
        
        Args:
            property_data: Property data dictionary
            
        Returns:
            True if property passes filters, False otherwise
        """
        
        if not self.config.get('enable_filtering', False):
            return True  # No filtering enabled, include all properties
        
        try:
            # Price filtering
            price_filter = self.config.get('price_filter', {})
            if price_filter.get('min') or price_filter.get('max'):
                price_text = property_data.get('price', '').lower()
                price_value = self.extract_numeric_price(price_text)
                
                if price_value:
                    if price_filter.get('min') and price_value < price_filter['min']:
                        return False
                    if price_filter.get('max') and price_value > price_filter['max']:
                        return False
            
            # Area filtering
            area_filter = self.config.get('area_filter', {})
            if area_filter.get('min') or area_filter.get('max'):
                area_text = property_data.get('area', '').lower()
                area_value = self.extract_numeric_area(area_text)
                
                if area_value:
                    if area_filter.get('min') and area_value < area_filter['min']:
                        return False
                    if area_filter.get('max') and area_value > area_filter['max']:
                        return False
            
            # Property type filtering
            property_type_filter = self.config.get('property_type_filter', [])
            if property_type_filter:
                property_type = property_data.get('property_type', '').lower()
                if not any(ptype.lower() in property_type for ptype in property_type_filter):
                    return False
            
            # BHK filtering
            bhk_filter = self.config.get('bhk_filter', [])
            if bhk_filter:
                title = property_data.get('title', '').lower()
                area = property_data.get('area', '').lower()
                combined_text = f"{title} {area}"
                
                bhk_found = False
                for bhk in bhk_filter:
                    if bhk.lower() in combined_text or f"{bhk} bhk" in combined_text:
                        bhk_found = True
                        break
                
                if not bhk_found:
                    return False
            
            # Location filtering
            location_filter = self.config.get('location_filter', [])
            if location_filter:
                locality = property_data.get('locality', '').lower()
                society = property_data.get('society', '').lower()
                combined_location = f"{locality} {society}"
                
                location_found = False
                for location in location_filter:
                    if location.lower() in combined_location:
                        location_found = True
                        break
                
                if not location_found:
                    return False
            
            # Exclude keywords filtering
            exclude_keywords = self.config.get('exclude_keywords', [])
            if exclude_keywords:
                title = property_data.get('title', '').lower()
                description = property_data.get('description', '').lower()
                combined_text = f"{title} {description}"
                
                for keyword in exclude_keywords:
                    if keyword.lower() in combined_text:
                        return False
            
            return True  # Passed all filters
            
        except Exception as e:
            self.logger.warning(f"Error applying filters: {str(e)}")
            return True  # Include property if filtering fails
    
    def extract_numeric_price(self, price_text: str) -> Optional[float]:
        """
        Extract numeric price value from price text
        
        Args:
            price_text: Price text string
            
        Returns:
            Numeric price value or None
        """
        
        # Remove common currency symbols and text
        price_text = re.sub(r'[₹,\s]', '', price_text)
        
        # Extract numbers and handle units (lakh, crore)
        if 'crore' in price_text.lower():
            numbers = re.findall(r'(\d+\.?\d*)', price_text)
            if numbers:
                return float(numbers[0]) * 10000000  # Convert crores to actual value
        elif 'lakh' in price_text.lower():
            numbers = re.findall(r'(\d+\.?\d*)', price_text)
            if numbers:
                return float(numbers[0]) * 100000  # Convert lakhs to actual value
        else:
            numbers = re.findall(r'(\d+\.?\d*)', price_text)
            if numbers:
                return float(numbers[0])
        
        return None
    
    def extract_numeric_area(self, area_text: str) -> Optional[float]:
        """
        Extract numeric area value from area text
        
        Args:
            area_text: Area text string
            
        Returns:
            Numeric area value or None
        """
        
        # Extract numbers from area text
        numbers = re.findall(r'(\d+\.?\d*)', area_text)
        if numbers:
            return float(numbers[0])
        
        return None
    
    def get_filtered_properties_count(self) -> Dict[str, int]:
        """
        Get count of properties before and after filtering
        
        Returns:
            Dictionary with filter statistics
        """
        return self._filter_stats.copy()
    
    def update_filter_stats(self, total: int = 0, filtered: int = 0, excluded: int = 0):
        """
        Update filter statistics
        
        Args:
            total: Total properties processed
            filtered: Properties that passed filters
            excluded: Properties that were excluded
        """
        self._filter_stats['total'] += total
        self._filter_stats['filtered'] += filtered
        self._filter_stats['excluded'] += excluded
    
    def reset_filter_stats(self):
        """Reset filter statistics"""
        self._filter_stats = {
            'total': 0,
            'filtered': 0,
            'excluded': 0
        }

