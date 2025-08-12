#!/usr/bin/env python3
"""
Property Extraction Analysis
Analyzes the scraper's ability to extract all 30 properties from a page
"""

import sys
import os
from bs4 import BeautifulSoup

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from integrated_magicbricks_scraper import IntegratedMagicBricksScraper

def analyze_property_extraction():
    """
    Comprehensive analysis of property extraction capabilities
    """
    
    print("🔍 PROPERTY EXTRACTION ANALYSIS")
    print("=" * 60)
    
    # Read the saved HTML file
    html_file = "debug_bot_detection.html"
    if not os.path.exists(html_file):
        print(f"❌ HTML file {html_file} not found")
        return
    
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Create scraper instance
    scraper = IntegratedMagicBricksScraper(headless=True)
    
    print("\n📊 STEP 1: Property Card Detection")
    print("-" * 40)
    
    # Find property cards
    property_cards = scraper._find_property_cards(soup)
    print(f"✅ Found {len(property_cards)} property cards")
    
    print("\n📊 STEP 2: Property Data Extraction")
    print("-" * 40)
    
    extracted_properties = []
    failed_extractions = []
    
    for i, card in enumerate(property_cards):
        try:
            # Extract property data
            property_data = scraper.extract_property_data(card, 1, i + 1)
            
            if property_data:
                # Validate and clean the data
                cleaned_data = scraper._validate_and_clean_property_data(property_data)
                
                # Apply filters
                if scraper._apply_property_filters(cleaned_data):
                    extracted_properties.append(cleaned_data)
                    print(f"  ✅ Property {i+1:2d}: {cleaned_data.get('title', 'N/A')[:50]}...")
                else:
                    failed_extractions.append({
                        'index': i+1,
                        'reason': 'Filtered out',
                        'data': cleaned_data
                    })
                    print(f"  ❌ Property {i+1:2d}: Filtered out")
            else:
                failed_extractions.append({
                    'index': i+1,
                    'reason': 'No data extracted',
                    'data': None
                })
                print(f"  ❌ Property {i+1:2d}: No data extracted")
                
        except Exception as e:
            failed_extractions.append({
                'index': i+1,
                'reason': f'Exception: {str(e)}',
                'data': None
            })
            print(f"  ❌ Property {i+1:2d}: Exception - {str(e)}")
    
    print("\n📊 STEP 3: Analysis Results")
    print("-" * 40)
    
    print(f"📋 Total property cards found: {len(property_cards)}")
    print(f"✅ Successfully extracted: {len(extracted_properties)}")
    print(f"❌ Failed extractions: {len(failed_extractions)}")
    print(f"📈 Success rate: {(len(extracted_properties)/len(property_cards)*100):.1f}%")
    
    if failed_extractions:
        print("\n📊 STEP 4: Failure Analysis")
        print("-" * 40)
        
        failure_reasons = {}
        for failure in failed_extractions:
            reason = failure['reason']
            if 'Exception' in reason:
                reason = 'Exception during extraction'
            elif 'Filtered' in reason:
                reason = 'Filtered out by criteria'
            elif 'No data' in reason:
                reason = 'No valid data extracted'
            
            failure_reasons[reason] = failure_reasons.get(reason, 0) + 1
        
        print("Failure breakdown:")
        for reason, count in failure_reasons.items():
            print(f"  • {reason}: {count} properties")
        
        # Analyze specific failures
        print("\n🔍 Detailed failure analysis:")
        for failure in failed_extractions[:5]:  # Show first 5 failures
            print(f"\n  Property {failure['index']}:")
            print(f"    Reason: {failure['reason']}")
            if failure['data']:
                data = failure['data']
                print(f"    Title: {data.get('title', 'N/A')}")
                print(f"    Price: {data.get('price', 'N/A')}")
                print(f"    URL: {data.get('property_url', 'N/A')}")
                print(f"    Validation issues: {data.get('validation_issues', [])}")
    
    print("\n📊 STEP 5: Data Quality Analysis")
    print("-" * 40)
    
    if extracted_properties:
        # Analyze data quality
        quality_scores = [prop.get('data_quality_score', 0) for prop in extracted_properties]
        avg_quality = sum(quality_scores) / len(quality_scores)
        
        print(f"📈 Average data quality score: {avg_quality:.1f}%")
        
        # Field completeness
        essential_fields = ['title', 'price', 'area', 'property_url']
        print("\nField completeness:")
        for field in essential_fields:
            filled = len([p for p in extracted_properties if p.get(field) and str(p[field]).strip()])
            percentage = (filled / len(extracted_properties)) * 100
            print(f"  • {field}: {filled}/{len(extracted_properties)} ({percentage:.1f}%)")
    
    print("\n📊 STEP 6: Recommendations")
    print("-" * 40)
    
    success_rate = (len(extracted_properties)/len(property_cards)*100) if property_cards else 0
    
    if success_rate >= 90:
        print("✅ EXCELLENT: Scraper is extracting most properties successfully")
    elif success_rate >= 75:
        print("⚠️ GOOD: Scraper is working well but has room for improvement")
    elif success_rate >= 50:
        print("⚠️ MODERATE: Scraper needs optimization")
    else:
        print("❌ POOR: Scraper needs significant improvements")
    
    print("\nPotential improvements:")
    if len(failed_extractions) > 0:
        print("  • Review and update CSS selectors for failed extractions")
        print("  • Improve error handling for edge cases")
        print("  • Add more fallback extraction methods")
    
    if success_rate < 100:
        print("  • Analyze HTML structure of failed property cards")
        print("  • Add more robust data validation")
        print("  • Implement retry mechanisms for failed extractions")
    
    print("\n🎉 Analysis Complete!")
    print("=" * 60)

if __name__ == "__main__":
    analyze_property_extraction()