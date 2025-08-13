#!/usr/bin/env python3
"""
Test Enhanced Field Extraction
Tests the improved extraction for description, locality, society, and status
"""

from integrated_magicbricks_scraper import IntegratedMagicBricksScraper
import pandas as pd

def test_enhanced_field_extraction():
    """Test the enhanced field extraction improvements"""
    
    print('🔬 TESTING ENHANCED FIELD EXTRACTION')
    print('=' * 50)
    
    # Create scraper instance
    scraper = IntegratedMagicBricksScraper()
    
    print('📋 Scraping 2 pages to test enhanced field extraction...')
    result = scraper.scrape_properties_with_incremental(
        city='gurgaon',
        max_pages=2,
        export_formats=['csv']
    )
    
    if not scraper.properties:
        print('❌ No properties scraped')
        scraper.close()
        return
    
    print(f'✅ Scraped {len(scraper.properties)} properties')
    
    # Analyze field completeness
    total_properties = len(scraper.properties)
    
    # Critical fields to analyze
    critical_fields = {
        'description': 'Description',
        'locality': 'Locality', 
        'society': 'Society',
        'status': 'Status'
    }
    
    print(f'\n📊 ENHANCED FIELD EXTRACTION RESULTS:')
    print('=' * 50)
    
    improvements = {}
    
    for field_key, field_name in critical_fields.items():
        filled_count = sum(1 for prop in scraper.properties if prop.get(field_key) and str(prop.get(field_key)).strip())
        completeness = (filled_count / total_properties) * 100
        
        status_icon = '✅' if completeness >= 90 else '⚠️' if completeness >= 50 else '❌'
        print(f'   {status_icon} {field_name}: {completeness:.1f}% ({filled_count}/{total_properties})')
        
        improvements[field_key] = {
            'completeness': completeness,
            'filled': filled_count,
            'total': total_properties
        }
    
    # Show sample data for improved fields
    print(f'\n📝 SAMPLE DATA FOR ENHANCED FIELDS:')
    print('=' * 50)
    
    for i, prop in enumerate(scraper.properties[:5]):
        print(f'\n🏡 PROPERTY {i+1}:')
        title = prop.get('title', 'NO TITLE')
        print(f'   📝 Title: {title[:60]}...')
        
        for field_key, field_name in critical_fields.items():
            value = prop.get(field_key, '')
            status = '✅' if value and str(value).strip() else '❌'
            print(f'   {status} {field_name}: "{value}"')
    
    # Compare with previous results (if available)
    print(f'\n📈 IMPROVEMENT ANALYSIS:')
    print('=' * 50)
    
    # Previous results from our analysis
    previous_results = {
        'description': 0.0,
        'locality': 0.0,
        'society': 39.4,
        'status': 44.7
    }
    
    for field_key, field_name in critical_fields.items():
        current = improvements[field_key]['completeness']
        previous = previous_results.get(field_key, 0.0)
        improvement = current - previous
        
        if improvement > 0:
            print(f'   📈 {field_name}: {previous:.1f}% → {current:.1f}% (+{improvement:.1f}%)')
        elif improvement < 0:
            print(f'   📉 {field_name}: {previous:.1f}% → {current:.1f}% ({improvement:.1f}%)')
        else:
            print(f'   ➡️ {field_name}: {current:.1f}% (no change)')
    
    # Save enhanced results
    df = pd.DataFrame(scraper.properties)
    df.to_csv('enhanced_field_extraction_results.csv', index=False)
    print(f'\n💾 Saved enhanced results to: enhanced_field_extraction_results.csv')
    
    # Overall assessment
    print(f'\n🎯 OVERALL ASSESSMENT:')
    print('=' * 50)
    
    total_improvement = sum(improvements[field]['completeness'] for field in critical_fields.keys())
    average_completeness = total_improvement / len(critical_fields)
    
    print(f'📊 Average field completeness: {average_completeness:.1f}%')
    
    if average_completeness >= 75:
        print('🎉 EXCELLENT: Field extraction significantly improved!')
    elif average_completeness >= 50:
        print('✅ GOOD: Substantial improvement in field extraction')
    elif average_completeness >= 25:
        print('⚠️ MODERATE: Some improvement, but more work needed')
    else:
        print('❌ POOR: Field extraction still needs significant work')
    
    # Specific recommendations
    print(f'\n📋 RECOMMENDATIONS:')
    for field_key, field_name in critical_fields.items():
        completeness = improvements[field_key]['completeness']
        if completeness < 50:
            print(f'   🔧 {field_name}: Needs further enhancement (only {completeness:.1f}% complete)')
        elif completeness < 90:
            print(f'   🔧 {field_name}: Good progress, minor refinements needed ({completeness:.1f}% complete)')
        else:
            print(f'   ✅ {field_name}: Excellent extraction rate ({completeness:.1f}% complete)')
    
    scraper.close()
    return improvements

if __name__ == "__main__":
    test_enhanced_field_extraction()
