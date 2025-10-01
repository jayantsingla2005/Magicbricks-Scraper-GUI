#!/usr/bin/env python3
"""
Integration Test for Refactored MagicBricks Scraper
Tests the complete scraping workflow with all modules integrated
"""

import sys
from pathlib import Path
from datetime import datetime

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from integrated_magicbricks_scraper import IntegratedMagicBricksScraper
from user_mode_options import ScrapingMode


def run_integration_test():
    """Run integration test with medium-scale scraping"""
    
    print("=" * 80)
    print("INTEGRATION TEST - Refactored MagicBricks Scraper")
    print("=" * 80)
    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Test configuration
    test_config = {
        'city': 'gurgaon',
        'mode': ScrapingMode.INCREMENTAL,
        'max_pages': 3,  # Small test - 3 pages (~90 properties)
        'headless': True,
        'incremental_enabled': True,
        'individual_pages': False,  # Skip individual pages for faster test
        'export_formats': ['csv', 'json']
    }
    
    print("📋 Test Configuration:")
    print(f"   City: {test_config['city']}")
    print(f"   Mode: {test_config['mode'].value}")
    print(f"   Max Pages: {test_config['max_pages']}")
    print(f"   Headless: {test_config['headless']}")
    print(f"   Incremental: {test_config['incremental_enabled']}")
    print(f"   Individual Pages: {test_config['individual_pages']}")
    print(f"   Export Formats: {', '.join(test_config['export_formats'])}")
    print()
    
    try:
        # Initialize scraper
        print("🔧 Initializing scraper...")
        scraper = IntegratedMagicBricksScraper(
            headless=test_config['headless'],
            incremental_enabled=test_config['incremental_enabled']
        )
        print("✅ Scraper initialized successfully")
        print()
        
        # Run scraping
        print("🚀 Starting scraping process...")
        print("-" * 80)
        
        result = scraper.scrape_properties_with_incremental(
            city=test_config['city'],
            mode=test_config['mode'],
            max_pages=test_config['max_pages'],
            include_individual_pages=test_config['individual_pages'],
            export_formats=test_config['export_formats']
        )
        
        print("-" * 80)
        print()
        
        # Analyze results
        if result['success']:
            print("✅ INTEGRATION TEST PASSED")
            print()
            print("📊 Test Results:")
            print(f"   Total Properties: {result.get('total_properties', 0)}")
            print(f"   Pages Scraped: {result.get('pages_scraped', 0)}")
            print(f"   Duration: {result.get('duration', 'N/A')}")
            print(f"   Data Quality: {result.get('data_quality_score', 0):.1f}%")
            
            if 'export_files' in result:
                print()
                print("📁 Exported Files:")
                for format_type, filepath in result['export_files'].items():
                    print(f"   {format_type.upper()}: {filepath}")
            
            print()
            print("🎯 Validation Checks:")
            
            # Check 1: Properties extracted
            if result.get('total_properties', 0) > 0:
                print("   ✅ Properties extracted successfully")
            else:
                print("   ❌ No properties extracted")
                return False
            
            # Check 2: Data quality
            if result.get('data_quality_score', 0) >= 70:
                print(f"   ✅ Data quality acceptable ({result.get('data_quality_score', 0):.1f}%)")
            else:
                print(f"   ⚠️ Data quality below threshold ({result.get('data_quality_score', 0):.1f}%)")
            
            # Check 3: Export files created
            if result.get('export_files'):
                print(f"   ✅ Export files created ({len(result['export_files'])} formats)")
            else:
                print("   ⚠️ No export files created")
            
            # Check 4: No critical errors
            if result.get('errors', 0) == 0:
                print("   ✅ No critical errors")
            else:
                print(f"   ⚠️ {result.get('errors', 0)} errors encountered")
            
            print()
            print("=" * 80)
            print("INTEGRATION TEST COMPLETED SUCCESSFULLY")
            print("=" * 80)
            return True
            
        else:
            print("❌ INTEGRATION TEST FAILED")
            print()
            print(f"Error: {result.get('error', 'Unknown error')}")
            print()
            print("=" * 80)
            return False
            
    except Exception as e:
        print()
        print("❌ INTEGRATION TEST FAILED WITH EXCEPTION")
        print()
        print(f"Exception: {str(e)}")
        print()
        import traceback
        traceback.print_exc()
        print()
        print("=" * 80)
        return False


if __name__ == '__main__':
    success = run_integration_test()
    sys.exit(0 if success else 1)

