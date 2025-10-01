#!/usr/bin/env python3
"""
Unit Tests for PropertyExtractor Module
Tests all extraction methods, fallback strategies, and edge cases
"""

import unittest
import sys
from pathlib import Path
from bs4 import BeautifulSoup
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scraper.property_extractor import PropertyExtractor


class TestPropertyExtractor(unittest.TestCase):
    """Test suite for PropertyExtractor class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.premium_selectors = {
            'title': ['h2', '.mb-srp__card__title', '*[class*="title"]'],
            'price': ['.mb-srp__card__price', '*[class*="price"]'],
            'area': ['.mb-srp__card__summary__list', '*[class*="area"]'],
            'url': ['a[href*="magicbricks.com"]']
        }
        
        self.extractor = PropertyExtractor(
            premium_selectors=self.premium_selectors,
            date_parser=None,
            logger=None
        )
    
    def test_initialization(self):
        """Test PropertyExtractor initialization"""
        self.assertIsNotNone(self.extractor)
        self.assertEqual(self.extractor.premium_selectors, self.premium_selectors)
        self.assertEqual(self.extractor.extraction_stats['total_extracted'], 0)
    
    def test_extract_property_data_valid_card(self):
        """Test extraction with valid property card"""
        html = """
        <div class="mb-srp__card">
            <h2>3 BHK Apartment for Sale in Sector 88A</h2>
            <div class="mb-srp__card__price">₹ 1.2 Crore</div>
            <div class="mb-srp__card__summary__list">1500 sqft</div>
            <a href="https://www.magicbricks.com/property-123">View Details</a>
        </div>
        """
        card = BeautifulSoup(html, 'html.parser')
        
        result = self.extractor.extract_property_data(card, 1, 1)
        
        self.assertIsNotNone(result)
        self.assertIn('title', result)
        self.assertIn('price', result)
        self.assertIn('area', result)
        self.assertEqual(result['page_number'], 1)
        self.assertEqual(result['property_index'], 1)
    
    def test_extract_property_data_missing_fields(self):
        """Test extraction with missing fields"""
        html = """
        <div class="mb-srp__card">
            <h2>Property Title Only</h2>
        </div>
        """
        card = BeautifulSoup(html, 'html.parser')
        
        result = self.extractor.extract_property_data(card, 1, 1)
        
        # Should still extract with lenient validation
        self.assertIsNotNone(result)
        self.assertIn('title', result)
    
    def test_extract_property_data_empty_card(self):
        """Test extraction with empty card"""
        html = "<div class='mb-srp__card'></div>"
        card = BeautifulSoup(html, 'html.parser')
        
        result = self.extractor.extract_property_data(card, 1, 1)
        
        # Should return None for completely empty card
        self.assertIsNone(result)
    
    def test_detect_premium_property_type_standard(self):
        """Test premium detection for standard property"""
        html = """
        <div class="mb-srp__card">
            <h2>Standard Property</h2>
        </div>
        """
        card = BeautifulSoup(html, 'html.parser')
        
        result = self.extractor.detect_premium_property_type(card)
        
        self.assertFalse(result['is_premium'])
        self.assertEqual(result['premium_type'], 'standard')
    
    def test_detect_premium_property_type_premium(self):
        """Test premium detection for premium property"""
        html = """
        <div class="mb-srp__card mb-srp__card--premium">
            <h2>Premium Property</h2>
            <span class="premium-badge">Premium</span>
        </div>
        """
        card = BeautifulSoup(html, 'html.parser')
        
        result = self.extractor.detect_premium_property_type(card)
        
        self.assertTrue(result['is_premium'])
        self.assertIn('premium', result['premium_type'].lower())
    
    def test_extract_with_enhanced_fallback_success(self):
        """Test enhanced fallback extraction - success case"""
        html = """
        <div>
            <h2>Test Title</h2>
        </div>
        """
        card = BeautifulSoup(html, 'html.parser')
        
        result = self.extractor._extract_with_enhanced_fallback(
            card, ['h2'], 'title', 'N/A'
        )
        
        self.assertEqual(result, 'Test Title')
    
    def test_extract_with_enhanced_fallback_default(self):
        """Test enhanced fallback extraction - default case"""
        html = "<div></div>"
        card = BeautifulSoup(html, 'html.parser')
        
        result = self.extractor._extract_with_enhanced_fallback(
            card, ['h2'], 'title', 'N/A'
        )
        
        self.assertEqual(result, 'N/A')
    
    def test_extract_premium_property_url_valid(self):
        """Test URL extraction with valid URL"""
        html = """
        <div>
            <a href="https://www.magicbricks.com/property-123">Link</a>
        </div>
        """
        card = BeautifulSoup(html, 'html.parser')
        
        result = self.extractor._extract_premium_property_url(card)
        
        self.assertIn('magicbricks.com', result)
    
    def test_extract_premium_property_url_relative(self):
        """Test URL extraction with relative URL (fallback path)"""
        # Update selectors to allow any href for this test
        test_selectors = {
            'url': ['a[href]']  # More permissive selector
        }
        test_extractor = PropertyExtractor(
            premium_selectors=test_selectors,
            date_parser=None,
            logger=None
        )

        html = """
        <div>
            <a href="/propertydetail/property-123">Link</a>
        </div>
        """
        card = BeautifulSoup(html, 'html.parser')

        result = test_extractor._extract_premium_property_url(card)

        # Should convert to absolute URL
        self.assertIn('magicbricks.com', result)
    
    def test_extraction_statistics_tracking(self):
        """Test that statistics are properly tracked"""
        html = """
        <div class="mb-srp__card">
            <h2>Test Property</h2>
            <div class="mb-srp__card__price">₹ 1 Cr</div>
            <div class="mb-srp__card__summary__list">1000 sqft</div>
        </div>
        """
        card = BeautifulSoup(html, 'html.parser')
        
        initial_total = self.extractor.extraction_stats['total_extracted']
        
        self.extractor.extract_property_data(card, 1, 1)
        
        self.assertEqual(
            self.extractor.extraction_stats['total_extracted'],
            initial_total + 1
        )
    
    def test_get_extraction_statistics(self):
        """Test statistics retrieval"""
        stats = self.extractor.get_extraction_statistics()
        
        self.assertIn('total_extracted', stats)
        self.assertIn('successful_extractions', stats)
        self.assertIn('failed_extractions', stats)
        self.assertIn('premium_properties', stats)
        self.assertIn('standard_properties', stats)
    
    def test_reset_extraction_statistics(self):
        """Test statistics reset"""
        # Extract something first
        html = """
        <div class="mb-srp__card">
            <h2>Test</h2>
            <div class="mb-srp__card__price">₹ 1 Cr</div>
        </div>
        """
        card = BeautifulSoup(html, 'html.parser')
        self.extractor.extract_property_data(card, 1, 1)
        
        # Reset
        self.extractor.reset_extraction_statistics()
        
        # Verify reset
        stats = self.extractor.get_extraction_statistics()
        self.assertEqual(stats['total_extracted'], 0)
        self.assertEqual(stats['successful_extractions'], 0)
    
    def test_extract_property_type_from_title(self):
        """Test property type extraction from title"""
        test_cases = [
            ("3 BHK Apartment for Sale", "3 BHK"),
            ("4 BHK Villa in Sector 88", "4 BHK"),
            ("Studio Apartment", "Studio"),
            ("Independent House", "House"),
            ("Plot for Sale", "Plot"),
        ]
        
        for title, expected_type in test_cases:
            result = self.extractor._extract_property_type_from_title(title)
            self.assertIn(expected_type.lower(), result.lower())
    
    def test_special_characters_handling(self):
        """Test handling of special characters in data"""
        html = """
        <div class="mb-srp__card">
            <h2>Property with Special Chars: @#$%^&*()</h2>
            <div class="mb-srp__card__price">₹ 1.5 Crore</div>
        </div>
        """
        card = BeautifulSoup(html, 'html.parser')
        
        result = self.extractor.extract_property_data(card, 1, 1)
        
        self.assertIsNotNone(result)
        self.assertIn('title', result)


if __name__ == '__main__':
    unittest.main()

