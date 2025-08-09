#!/usr/bin/env python3
"""
Enhanced Selector Testing Script
Tests the improved selectors across different property types based on comprehensive research findings.
"""

import sys
import os
import json
from pathlib import Path

# Add src directory to path
sys.path.append(str(Path(__file__).parent / 'src'))

# Import with proper module path
from src.core.modern_scraper import ModernMagicBricksScraper
from src.utils.logger import ScraperLogger

def test_property_type_extraction():
    """Test enhanced extraction across different property types"""
    
    logger = ScraperLogger("enhanced_selector_test")
    logger.info("🔬 Starting Enhanced Selector Testing")

    # Test URLs for different property types
    test_urls = {
        "apartments": "https://www.magicbricks.com/flats-in-gurgaon-for-sale-pppfs",
        "houses": "https://www.magicbricks.com/independent-house-for-sale-in-gurgaon-pppfs",
        "plots": "https://www.magicbricks.com/residential-plots-land-for-sale-in-gurgaon-pppfs"
    }

    scraper = ModernMagicBricksScraper()
    results = {}
    
    for property_type, url in test_urls.items():
        logger.info(f"\n🏠 Testing {property_type.upper()} extraction...")
        logger.info(f"URL: {url}")
        
        try:
            # Update the scraper's base URL for this property type
            scraper.config['base_url'] = url

            # Scrape first page only for testing
            result = scraper.scrape_all_pages(start_page=1, max_pages=1)
            properties = result.get('properties', [])

            if not properties:
                logger.error(f"❌ No properties found for {property_type}")
                continue
            
            # Analyze extraction results
            total_properties = len(properties)
            area_extracted = sum(1 for p in properties if p.super_area or p.carpet_area)
            status_extracted = sum(1 for p in properties if p.status)
            society_extracted = sum(1 for p in properties if p.society)
            price_extracted = sum(1 for p in properties if p.price)
            
            # Calculate success rates
            area_rate = (area_extracted / total_properties) * 100 if total_properties > 0 else 0
            status_rate = (status_extracted / total_properties) * 100 if total_properties > 0 else 0
            society_rate = (society_extracted / total_properties) * 100 if total_properties > 0 else 0
            price_rate = (price_extracted / total_properties) * 100 if total_properties > 0 else 0
            
            results[property_type] = {
                "total_properties": total_properties,
                "extraction_rates": {
                    "area": f"{area_rate:.1f}%",
                    "status": f"{status_rate:.1f}%", 
                    "society": f"{society_rate:.1f}%",
                    "price": f"{price_rate:.1f}%"
                },
                "sample_data": []
            }
            
            # Collect sample data for analysis
            for i, prop in enumerate(properties[:5]):  # First 5 properties
                sample = {
                    "title": prop.title,
                    "super_area": prop.super_area,
                    "carpet_area": prop.carpet_area,
                    "status": prop.status,
                    "society": prop.society,
                    "price": prop.price
                }
                results[property_type]["sample_data"].append(sample)
            
            logger.info(f"✅ {property_type.capitalize()} Results:")
            logger.info(f"   📊 Total Properties: {total_properties}")
            logger.info(f"   📏 Area Extraction: {area_rate:.1f}%")
            logger.info(f"   🏷️  Status Extraction: {status_rate:.1f}%")
            logger.info(f"   🏢 Society Extraction: {society_rate:.1f}%")
            logger.info(f"   💰 Price Extraction: {price_rate:.1f}%")
            
            # Show sample extractions
            logger.info(f"   📋 Sample Extractions:")
            for i, sample in enumerate(results[property_type]["sample_data"][:3]):
                logger.info(f"      {i+1}. {sample['title'][:50]}...")
                logger.info(f"         Area: {sample['super_area'] or sample['carpet_area'] or 'N/A'}")
                logger.info(f"         Status: {sample['status'] or 'N/A'}")
                logger.info(f"         Society: {sample['society'] or 'N/A'}")
                
        except Exception as e:
            logger.error(f"❌ Error testing {property_type}: {str(e)}")
            results[property_type] = {"error": str(e)}
    
    # Generate summary report
    logger.info("\n" + "="*80)
    logger.info("📊 ENHANCED SELECTOR TESTING SUMMARY")
    logger.info("="*80)
    
    for property_type, data in results.items():
        if "error" in data:
            logger.info(f"❌ {property_type.upper()}: ERROR - {data['error']}")
        else:
            logger.info(f"✅ {property_type.upper()}:")
            logger.info(f"   Properties: {data['total_properties']}")
            logger.info(f"   Area: {data['extraction_rates']['area']}")
            logger.info(f"   Status: {data['extraction_rates']['status']}")
            logger.info(f"   Society: {data['extraction_rates']['society']}")
            logger.info(f"   Price: {data['extraction_rates']['price']}")
    
    # Save detailed results
    output_file = "enhanced_selector_test_results.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    logger.info(f"\n💾 Detailed results saved to: {output_file}")
    logger.info("🎯 Enhanced Selector Testing Complete!")
    
    return results

def analyze_property_type_patterns(results):
    """Analyze patterns across property types"""

    logger = ScraperLogger("pattern_analysis")
    logger.info("\n🔍 PROPERTY TYPE PATTERN ANALYSIS")
    logger.info("="*60)
    
    for property_type, data in results.items():
        if "error" in data:
            continue
            
        logger.info(f"\n📋 {property_type.upper()} PATTERNS:")
        
        # Analyze area field usage
        super_area_count = 0
        carpet_area_count = 0
        area_units = {}
        
        for sample in data.get("sample_data", []):
            if sample.get("super_area"):
                super_area_count += 1
                # Extract unit
                area_text = sample["super_area"]
                if "sqft" in area_text.lower():
                    area_units["sqft"] = area_units.get("sqft", 0) + 1
                elif "sqyrd" in area_text.lower():
                    area_units["sqyrd"] = area_units.get("sqyrd", 0) + 1
                    
            if sample.get("carpet_area"):
                carpet_area_count += 1
                area_text = sample["carpet_area"]
                if "sqft" in area_text.lower():
                    area_units["sqft"] = area_units.get("sqft", 0) + 1
                elif "sqyrd" in area_text.lower():
                    area_units["sqyrd"] = area_units.get("sqyrd", 0) + 1
        
        logger.info(f"   📏 Area Field Usage:")
        logger.info(f"      Super Area: {super_area_count}/5 samples")
        logger.info(f"      Carpet Area: {carpet_area_count}/5 samples")
        logger.info(f"   📐 Units Found: {area_units}")
        
        # Analyze status patterns
        status_patterns = {}
        for sample in data.get("sample_data", []):
            status = sample.get("status")
            if status:
                status_patterns[status] = status_patterns.get(status, 0) + 1
        
        logger.info(f"   🏷️  Status Patterns: {status_patterns}")

if __name__ == "__main__":
    print("🚀 Enhanced Selector Testing Script")
    print("Testing improved selectors across property types...")
    
    try:
        results = test_property_type_extraction()
        analyze_property_type_patterns(results)
        
        print("\n✅ Testing completed successfully!")
        print("📄 Check enhanced_selector_test_results.json for detailed results")
        
    except Exception as e:
        print(f"❌ Testing failed: {str(e)}")
        sys.exit(1)
