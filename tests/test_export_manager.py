#!/usr/bin/env python3
"""
Unit Tests for ExportManager Module
Tests CSV, JSON, and Excel export functionality
"""

import unittest
import sys
import os
import json
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scraper.export_manager import ExportManager


class TestExportManager(unittest.TestCase):
    """Test suite for ExportManager class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.manager = ExportManager(logger=None)
        self.test_properties = [
            {
                'title': '3 BHK Apartment',
                'price': '₹ 1.2 Crore',
                'area': '1500 sqft',
                'location': 'Sector 88A, Gurgaon',
                'url': 'https://www.magicbricks.com/property-123'
            },
            {
                'title': '4 BHK Villa',
                'price': '₹ 2.5 Crore',
                'area': '2500 sqft',
                'location': 'DLF Phase 5, Gurgaon',
                'url': 'https://www.magicbricks.com/property-456'
            }
        ]
        self.test_stats = {
            'total_properties': 2,
            'pages_scraped': 1,
            'success_rate': 100.0
        }
        
        # Clean up test files
        self.test_files = []
    
    def tearDown(self):
        """Clean up test files"""
        for filepath in self.test_files:
            if os.path.exists(filepath):
                try:
                    os.remove(filepath)
                except:
                    pass
    
    def test_initialization(self):
        """Test ExportManager initialization"""
        self.assertIsNotNone(self.manager)
    
    def test_save_to_csv_success(self):
        """Test successful CSV export"""
        filename = 'test_export.csv'
        self.test_files.append(filename)
        
        df, filepath = self.manager.save_to_csv(
            self.test_properties,
            self.test_stats,
            filename
        )
        
        self.assertIsNotNone(df)
        self.assertIsNotNone(filepath)
        self.assertTrue(os.path.exists(filepath))
        self.assertEqual(len(df), 2)
    
    def test_save_to_csv_empty_properties(self):
        """Test CSV export with empty properties list"""
        filename = 'test_empty.csv'
        self.test_files.append(filename)

        df, filepath = self.manager.save_to_csv(
            [],
            self.test_stats,
            filename
        )

        # Should return None for empty list
        self.assertIsNone(df)
        self.assertIsNone(filepath)
    
    def test_save_to_json_success(self):
        """Test successful JSON export"""
        filename = 'test_export.json'
        self.test_files.append(filename)
        
        json_data, filepath = self.manager.save_to_json(
            self.test_properties,
            self.test_stats,
            filename
        )
        
        self.assertIsNotNone(json_data)
        self.assertIsNotNone(filepath)
        self.assertTrue(os.path.exists(filepath))
        self.assertIn('metadata', json_data)
        self.assertIn('properties', json_data)
        self.assertEqual(len(json_data['properties']), 2)
    
    def test_save_to_json_metadata(self):
        """Test JSON export includes proper metadata"""
        filename = 'test_metadata.json'
        self.test_files.append(filename)
        
        json_data, filepath = self.manager.save_to_json(
            self.test_properties,
            self.test_stats,
            filename
        )
        
        metadata = json_data['metadata']
        self.assertIn('scrape_timestamp', metadata)
        self.assertIn('total_properties', metadata)
        self.assertIn('session_stats', metadata)
        self.assertIn('scraper_version', metadata)
        self.assertEqual(metadata['total_properties'], 2)
    
    def test_save_to_json_empty_properties(self):
        """Test JSON export with empty properties list"""
        filename = 'test_empty.json'
        self.test_files.append(filename)

        json_data, filepath = self.manager.save_to_json(
            [],
            self.test_stats,
            filename
        )

        # Should return None for empty list
        self.assertIsNone(json_data)
        self.assertIsNone(filepath)
    
    def test_save_to_excel_success(self):
        """Test successful Excel export"""
        filename = 'test_export.xlsx'
        self.test_files.append(filename)
        
        df, filepath = self.manager.save_to_excel(
            self.test_properties,
            self.test_stats,
            filename
        )
        
        self.assertIsNotNone(df)
        self.assertIsNotNone(filepath)
        self.assertTrue(os.path.exists(filepath))
    
    def test_export_data_multi_format(self):
        """Test multi-format export"""
        base_filename = 'test_multi'
        self.test_files.extend([
            f'{base_filename}.csv',
            f'{base_filename}.json',
            f'{base_filename}.xlsx'
        ])

        results = self.manager.export_data(
            self.test_properties,
            self.test_stats,
            formats=['csv', 'json', 'excel'],
            base_filename=base_filename
        )

        self.assertIn('csv', results)
        self.assertIn('json', results)
        self.assertIn('excel', results)
        # Results is a dict mapping format to filename, not success status
        self.assertIsNotNone(results['csv'])
        self.assertIsNotNone(results['json'])
        self.assertIsNotNone(results['excel'])
    
    def test_export_data_single_format(self):
        """Test single format export"""
        base_filename = 'test_single'
        self.test_files.append(f'{base_filename}.csv')

        results = self.manager.export_data(
            self.test_properties,
            self.test_stats,
            formats=['csv'],
            base_filename=base_filename
        )

        self.assertIn('csv', results)
        self.assertIsNotNone(results['csv'])
    
    def test_default_filename_generation(self):
        """Test default filename generation"""
        df, filepath = self.manager.save_to_csv(
            self.test_properties,
            self.test_stats
        )
        
        self.test_files.append(filepath)
        self.assertIsNotNone(filepath)
        self.assertTrue(filepath.startswith('magicbricks_'))
        self.assertTrue(filepath.endswith('.csv'))
    
    def test_csv_column_order(self):
        """Test CSV maintains proper column order"""
        filename = 'test_columns.csv'
        self.test_files.append(filename)
        
        df, filepath = self.manager.save_to_csv(
            self.test_properties,
            self.test_stats,
            filename
        )
        
        # Check that important columns exist
        self.assertIn('title', df.columns)
        self.assertIn('price', df.columns)
        self.assertIn('area', df.columns)
    
    def test_json_file_validity(self):
        """Test JSON file is valid and parseable"""
        filename = 'test_valid.json'
        self.test_files.append(filename)
        
        json_data, filepath = self.manager.save_to_json(
            self.test_properties,
            self.test_stats,
            filename
        )
        
        # Read back and verify
        with open(filepath, 'r', encoding='utf-8') as f:
            loaded_data = json.load(f)
        
        self.assertEqual(loaded_data['metadata']['total_properties'], 2)
        self.assertEqual(len(loaded_data['properties']), 2)


if __name__ == '__main__':
    unittest.main()

