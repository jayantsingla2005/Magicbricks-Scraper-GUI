#!/usr/bin/env python3
"""
Unit Tests for DataValidator Module
Tests data validation, cleaning, and filtering functionality
"""

import unittest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scraper.data_validator import DataValidator


class TestDataValidator(unittest.TestCase):
    """Test suite for DataValidator class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.config = {
            'min_price': 50,  # 50 lakhs
            'max_price': 500,  # 500 lakhs (5 crore)
            'min_area': 500,
            'max_area': 5000,
            'property_types': ['apartment', 'flat'],
            'bhk_types': ['2 BHK', '3 BHK'],
            'locations': ['Gurgaon', 'Delhi'],
            'exclude_keywords': ['under construction']
        }
        self.validator = DataValidator(config=self.config, logger=None)
    
    def test_initialization(self):
        """Test DataValidator initialization"""
        self.assertIsNotNone(self.validator)
        self.assertEqual(self.validator.config, self.config)
    
    def test_validate_and_clean_valid_data(self):
        """Test validation and cleaning with valid data"""
        property_data = {
            'title': '  3 BHK Apartment  ',
            'price': '₹ 1.2 Crore',
            'area': '1500 sqft',
            'url': 'https://www.magicbricks.com/property-123',
            'location': 'Gurgaon'
        }
        
        result = self.validator.validate_and_clean_property_data(property_data)
        
        self.assertIsNotNone(result)
        self.assertEqual(result['title'], '3 BHK Apartment')  # Trimmed
        self.assertIn('data_quality_score', result)
        self.assertIn('validation_issues', result)
    
    def test_validate_and_clean_missing_fields(self):
        """Test validation with missing fields"""
        property_data = {
            'title': 'Test Property'
        }
        
        result = self.validator.validate_and_clean_property_data(property_data)
        
        self.assertIsNotNone(result)
        self.assertGreater(len(result['validation_issues']), 0)
    
    def test_extract_numeric_price_lakh(self):
        """Test numeric price extraction with lakh"""
        test_cases = [
            ('₹ 50 Lakh', 50.0),
            ('₹ 75.5 Lakh', 75.5),
            ('50 L', 50.0),
            ('₹ 1 Lakh', 1.0)
        ]
        
        for price_text, expected in test_cases:
            result = self.validator.extract_numeric_price(price_text)
            self.assertAlmostEqual(result, expected, places=1)
    
    def test_extract_numeric_price_crore(self):
        """Test numeric price extraction with crore"""
        test_cases = [
            ('₹ 1 Crore', 100.0),  # 1 crore = 100 lakhs
            ('₹ 2.5 Crore', 250.0),  # 2.5 crore = 250 lakhs
            ('1 Cr', 100.0),
            ('₹ 1.2 Cr', 120.0)
        ]
        
        for price_text, expected in test_cases:
            result = self.validator.extract_numeric_price(price_text)
            self.assertAlmostEqual(result, expected, places=1)
    
    def test_extract_numeric_price_invalid(self):
        """Test numeric price extraction with invalid input"""
        result = self.validator.extract_numeric_price('Price on Request')
        self.assertIsNone(result)
    
    def test_extract_numeric_area_sqft(self):
        """Test numeric area extraction"""
        test_cases = [
            ('1500 sqft', 1500.0),
            ('2,500 sq.ft', 2500.0),
            ('1000 Sq-ft', 1000.0),
            ('750 sq ft', 750.0)
        ]
        
        for area_text, expected in test_cases:
            result = self.validator.extract_numeric_area(area_text)
            self.assertAlmostEqual(result, expected, places=1)
    
    def test_extract_numeric_area_invalid(self):
        """Test numeric area extraction with invalid input"""
        result = self.validator.extract_numeric_area('N/A')
        self.assertIsNone(result)
    
    def test_apply_property_filters_pass(self):
        """Test property filtering - should pass"""
        property_data = {
            'title': '3 BHK Apartment in Gurgaon',
            'price': '₹ 1.2 Crore',  # 120 lakhs
            'area': '1500 sqft',
            'location': 'Sector 88A, Gurgaon'
        }
        
        result = self.validator.apply_property_filters(property_data)
        
        self.assertTrue(result)
    
    def test_apply_property_filters_price_too_low(self):
        """Test property filtering - price too low"""
        property_data = {
            'title': '2 BHK Apartment',
            'price': '₹ 30 Lakh',  # Below min_price (50)
            'area': '1000 sqft'
        }
        
        result = self.validator.apply_property_filters(property_data)
        
        self.assertFalse(result)
    
    def test_apply_property_filters_price_too_high(self):
        """Test property filtering - price too high"""
        property_data = {
            'title': '5 BHK Penthouse',
            'price': '₹ 10 Crore',  # 1000 lakhs, above max_price (500)
            'area': '5000 sqft'
        }
        
        result = self.validator.apply_property_filters(property_data)
        
        self.assertFalse(result)
    
    def test_apply_property_filters_area_too_small(self):
        """Test property filtering - area too small"""
        property_data = {
            'title': 'Studio Apartment',
            'price': '₹ 60 Lakh',
            'area': '300 sqft'  # Below min_area (500)
        }
        
        result = self.validator.apply_property_filters(property_data)
        
        self.assertFalse(result)
    
    def test_apply_property_filters_wrong_property_type(self):
        """Test property filtering - wrong property type"""
        property_data = {
            'title': 'Independent Villa',  # Not in property_types
            'price': '₹ 1.5 Crore',
            'area': '2000 sqft'
        }
        
        result = self.validator.apply_property_filters(property_data)
        
        self.assertFalse(result)
    
    def test_apply_property_filters_wrong_bhk(self):
        """Test property filtering - wrong BHK type"""
        property_data = {
            'title': '5 BHK Apartment',  # Not in bhk_types (2/3 BHK)
            'price': '₹ 2 Crore',
            'area': '3000 sqft'
        }
        
        result = self.validator.apply_property_filters(property_data)
        
        self.assertFalse(result)
    
    def test_apply_property_filters_excluded_keyword(self):
        """Test property filtering - excluded keyword"""
        property_data = {
            'title': '3 BHK Apartment Under Construction',
            'price': '₹ 1.2 Crore',
            'area': '1500 sqft'
        }
        
        result = self.validator.apply_property_filters(property_data)
        
        self.assertFalse(result)
    
    def test_apply_property_filters_no_config(self):
        """Test property filtering with no config (should pass all)"""
        validator_no_config = DataValidator(config={}, logger=None)
        
        property_data = {
            'title': 'Any Property',
            'price': '₹ 10 Lakh',
            'area': '100 sqft'
        }
        
        result = validator_no_config.apply_property_filters(property_data)
        
        self.assertTrue(result)
    
    def test_get_filter_statistics(self):
        """Test filter statistics retrieval"""
        # Apply some filters
        self.validator.apply_property_filters({'title': 'Test', 'price': '₹ 1 Cr'})
        
        stats = self.validator.get_filter_statistics()
        
        self.assertIn('total', stats)
        self.assertIn('filtered', stats)
        self.assertIn('excluded', stats)
    
    def test_reset_filter_statistics(self):
        """Test filter statistics reset"""
        # Apply some filters
        self.validator.apply_property_filters({'title': 'Test', 'price': '₹ 1 Cr'})
        
        # Reset
        self.validator.reset_filter_statistics()
        
        stats = self.validator.get_filter_statistics()
        self.assertEqual(stats['total'], 0)
        self.assertEqual(stats['filtered'], 0)


if __name__ == '__main__':
    unittest.main()

