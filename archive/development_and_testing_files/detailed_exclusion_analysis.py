#!/usr/bin/env python3
"""
Detailed Property Exclusion Analysis
Analyzes exactly why properties are being excluded during scraping
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from integrated_magicbricks_scraper import IntegratedMagicBricksScraper, ScrapingMode
import logging
from datetime import datetime

def analyze_property_exclusions():
    """Run detailed analysis of property exclusions"""
    
    print("🔍 DETAILED PROPERTY EXCLUSION ANALYSIS")
    print("=" * 50)
    
    try:
        # Initialize scraper with debug logging
        scraper = IntegratedMagicBricksScraper(headless=True, incremental_enabled=False)
        
        # Override the extract_property_data method to capture more details
        original_extract = scraper.extract_property_data
        original_validate = scraper._validate_extracted_data
        
        extraction_stats = {
            'total_cards_found': 0,
            'extraction_failed': 0,
            'validation_failed': 0,
            'filter_excluded': 0,
            'successfully_processed': 0,
            'failed_details': []
        }
        
        def detailed_extract_property_data(card, page_number, property_index):
            """Enhanced extraction with detailed logging"""
            extraction_stats['total_cards_found'] += 1
            
            try:
                result = original_extract(card, page_number, property_index)
                if result is None:
                    extraction_stats['extraction_failed'] += 1
                    
                    # Try to understand why extraction failed
                    title = scraper._extract_with_fallback(card, ['h2.mb-srp__card--title', 'h2[class*="title"]'], 'N/A')
                    price = scraper._extract_with_fallback(card, ['div.mb-srp__card__price--amount', 'span[class*="price"]'], 'N/A')
                    area = scraper._extract_with_fallback(card, ['div.mb-srp__card__summary--value', 'span[class*="area"]'], 'N/A')
                    url = scraper._extract_property_url(card)
                    
                    failure_reason = []
                    if not url:
                        failure_reason.append('No property URL found')
                    if title == 'N/A':
                        failure_reason.append('No title found')
                    if price == 'N/A':
                        failure_reason.append('No price found')
                    if area == 'N/A':
                        failure_reason.append('No area found')
                    
                    extraction_stats['failed_details'].append({
                        'page': page_number,
                        'index': property_index,
                        'reason': 'Extraction failed',
                        'details': failure_reason,
                        'title': title,
                        'price': price,
                        'area': area,
                        'url': url
                    })
                    
                    print(f"   ❌ Property {property_index} extraction failed: {', '.join(failure_reason)}")
                else:
                    extraction_stats['successfully_processed'] += 1
                    print(f"   ✅ Property {property_index} extracted successfully")
                    
                return result
                
            except Exception as e:
                extraction_stats['extraction_failed'] += 1
                extraction_stats['failed_details'].append({
                    'page': page_number,
                    'index': property_index,
                    'reason': 'Extraction exception',
                    'details': [str(e)]
                })
                print(f"   💥 Property {property_index} extraction exception: {str(e)}")
                return None
        
        def detailed_validate_extracted_data(property_data):
            """Enhanced validation with detailed logging"""
            result = original_validate(property_data)
            
            if not result:
                extraction_stats['validation_failed'] += 1
                
                # Analyze why validation failed
                essential_fields = ['title', 'price', 'area']
                additional_fields = ['amenities', 'description', 'builder_info', 'location_details']
                
                filled_essential = [field for field in essential_fields if property_data.get(field)]
                filled_additional = [field for field in additional_fields if property_data.get(field)]
                
                missing_essential = [field for field in essential_fields if not property_data.get(field)]
                missing_additional = [field for field in additional_fields if not property_data.get(field)]
                
                validation_details = {
                    'filled_essential': filled_essential,
                    'filled_additional': filled_additional,
                    'missing_essential': missing_essential,
                    'missing_additional': missing_additional,
                    'essential_count': len(filled_essential),
                    'additional_count': len(filled_additional)
                }
                
                extraction_stats['failed_details'].append({
                    'reason': 'Validation failed',
                    'details': validation_details,
                    'title': property_data.get('title', 'N/A')[:50],
                    'url': property_data.get('url', 'N/A')
                })
                
                print(f"   ⚠️ Validation failed - Essential: {len(filled_essential)}/3, Additional: {len(filled_additional)}/4")
                print(f"      Missing essential: {missing_essential}")
                print(f"      Missing additional: {missing_additional}")
            
            return result
        
        # Monkey patch the methods
        scraper.extract_property_data = detailed_extract_property_data
        scraper._validate_extracted_data = detailed_validate_extracted_data
        
        print("📊 Running analysis scrape (1 page max)...")
        
        result = scraper.scrape_properties_with_incremental(
            city="gurgaon",
            max_pages=1,  # Only 1 page for detailed analysis
            mode=ScrapingMode.FULL,
            export_formats=['csv'],
            include_individual_pages=False
        )
        
        print("\n📈 EXCLUSION ANALYSIS RESULTS")
        print("=" * 40)
        print(f"🔍 Total property cards found: {extraction_stats['total_cards_found']}")
        print(f"❌ Extraction failures: {extraction_stats['extraction_failed']}")
        print(f"⚠️ Validation failures: {extraction_stats['validation_failed']}")
        print(f"✅ Successfully processed: {extraction_stats['successfully_processed']}")
        
        if result.get('success'):
            filter_stats = scraper.get_filtered_properties_count()
            print(f"🚫 Filter exclusions: {filter_stats.get('excluded', 0)}")
            print(f"💾 Final saved count: {result.get('properties_scraped', 0)}")
        
        print("\n🔍 DETAILED FAILURE ANALYSIS")
        print("=" * 40)
        
        extraction_failures = [f for f in extraction_stats['failed_details'] if f['reason'] == 'Extraction failed']
        validation_failures = [f for f in extraction_stats['failed_details'] if f['reason'] == 'Validation failed']
        
        if extraction_failures:
            print(f"\n❌ EXTRACTION FAILURES ({len(extraction_failures)}):")
            for i, failure in enumerate(extraction_failures[:5], 1):  # Show first 5
                print(f"   {i}. Page {failure.get('page', '?')}, Index {failure.get('index', '?')}")
                print(f"      Issues: {', '.join(failure['details'])}")
                print(f"      Title: {failure.get('title', 'N/A')}")
                print(f"      Price: {failure.get('price', 'N/A')}")
                print(f"      Area: {failure.get('area', 'N/A')}")
                print(f"      URL: {'Found' if failure.get('url') else 'Missing'}")
                print()
        
        if validation_failures:
            print(f"\n⚠️ VALIDATION FAILURES ({len(validation_failures)}):")
            for i, failure in enumerate(validation_failures[:5], 1):  # Show first 5
                details = failure['details']
                print(f"   {i}. Title: {failure.get('title', 'N/A')}")
                print(f"      Essential fields ({details['essential_count']}/3): {details['filled_essential']}")
                print(f"      Additional fields ({details['additional_count']}/4): {details['filled_additional']}")
                print(f"      Missing essential: {details['missing_essential']}")
                print(f"      Missing additional: {details['missing_additional']}")
                print()
        
        print("\n💡 RECOMMENDATIONS:")
        if extraction_failures:
            common_issues = {}
            for failure in extraction_failures:
                for issue in failure['details']:
                    common_issues[issue] = common_issues.get(issue, 0) + 1
            
            print("   Most common extraction issues:")
            for issue, count in sorted(common_issues.items(), key=lambda x: x[1], reverse=True):
                print(f"   - {issue}: {count} occurrences")
        
        if validation_failures:
            missing_fields = {}
            for failure in validation_failures:
                for field in failure['details']['missing_essential'] + failure['details']['missing_additional']:
                    missing_fields[field] = missing_fields.get(field, 0) + 1
            
            print("   Most commonly missing fields:")
            for field, count in sorted(missing_fields.items(), key=lambda x: x[1], reverse=True):
                print(f"   - {field}: {count} occurrences")
        
        return extraction_stats
        
    except Exception as e:
        print(f"❌ Analysis failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return None
    
    finally:
        if 'scraper' in locals():
            scraper.close()

if __name__ == "__main__":
    analyze_property_exclusions()