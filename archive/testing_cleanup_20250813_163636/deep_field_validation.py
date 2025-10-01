#!/usr/bin/env python3
"""
Deep Field Validation using the working scraper approach
Tests ALL fields across different property types using the main scraper
"""

from integrated_magicbricks_scraper import IntegratedMagicBricksScraper
import pandas as pd
import time

def deep_field_validation():
    """Deep validation of all fields using the working scraper approach"""
    
    print('🔍 DEEP FIELD VALIDATION STARTING...')
    print('=' * 60)
    
    # Create scraper instance
    scraper = IntegratedMagicBricksScraper()
    
    # Test multiple cities to get diverse property types
    test_cities = ['gurgaon', 'noida', 'mumbai']
    
    all_results = []
    
    for city in test_cities:
        print(f'\n🏙️ TESTING CITY: {city.upper()}')
        print('-' * 40)
        
        try:
            # Use the working scraper method
            result = scraper.scrape_properties_with_incremental(
                city=city,
                max_pages=2,  # Test 2 pages to get variety
                export_formats=['csv']
            )
            
            if scraper.properties:
                print(f'✅ Successfully scraped {len(scraper.properties)} properties from {city}')
                
                # Analyze each property in detail
                for i, prop in enumerate(scraper.properties):
                    analysis = analyze_property_fields(prop, city, i+1)
                    all_results.append(analysis)
                    
                    # Print sample analysis for first few properties
                    if i < 3:
                        print(f'\n🏡 PROPERTY {i+1} ANALYSIS:')
                        print_property_analysis(analysis)
            else:
                print(f'❌ No properties scraped from {city}')
                
        except Exception as e:
            print(f'❌ Error testing {city}: {str(e)}')
    
    # Close scraper
    scraper.close()
    
    # Comprehensive analysis
    if all_results:
        df = pd.DataFrame(all_results)
        df.to_csv('deep_field_validation_results.csv', index=False)
        print(f'\n💾 Saved {len(all_results)} property analyses to deep_field_validation_results.csv')
        
        # Field completeness analysis
        print('\n📊 COMPREHENSIVE FIELD COMPLETENESS ANALYSIS:')
        print('=' * 60)
        
        field_analysis = {}
        for column in df.columns:
            if column not in ['city', 'property_index']:
                filled_count = df[column].notna().sum()
                non_empty_count = df[column].astype(str).str.strip().ne('').sum()
                completeness = (non_empty_count / len(df)) * 100
                field_analysis[column] = {
                    'completeness': completeness,
                    'filled': non_empty_count,
                    'total': len(df)
                }
                
                status = '✅' if completeness >= 90 else '⚠️' if completeness >= 50 else '❌'
                print(f'   {status} {column}: {completeness:.1f}% ({non_empty_count}/{len(df)})')
        
        # Property type analysis
        print('\n🏠 PROPERTY TYPE DISTRIBUTION:')
        print('-' * 40)
        if 'detected_property_type' in df.columns:
            type_counts = df['detected_property_type'].value_counts()
            for prop_type, count in type_counts.items():
                percentage = (count / len(df)) * 100
                print(f'   📊 {prop_type}: {count} properties ({percentage:.1f}%)')
        
        # Posted by analysis
        print('\n👤 POSTED BY ANALYSIS:')
        print('-' * 40)
        if 'posted_by_category' in df.columns:
            posted_by_counts = df['posted_by_category'].value_counts()
            for category, count in posted_by_counts.items():
                percentage = (count / len(df)) * 100
                print(f'   📊 {category}: {count} properties ({percentage:.1f}%)')
        
        # Critical missing fields
        print('\n🚨 CRITICAL MISSING FIELDS:')
        print('-' * 40)
        critical_fields = ['description', 'posted_by_category', 'property_type', 'status']
        for field in critical_fields:
            if field in field_analysis:
                if field_analysis[field]['completeness'] < 50:
                    print(f'   ❌ {field}: Only {field_analysis[field]["completeness"]:.1f}% complete')
                elif field_analysis[field]['completeness'] < 90:
                    print(f'   ⚠️ {field}: {field_analysis[field]["completeness"]:.1f}% complete (needs improvement)')
                else:
                    print(f'   ✅ {field}: {field_analysis[field]["completeness"]:.1f}% complete')
    
    return all_results

def analyze_property_fields(prop, city, index):
    """Detailed analysis of a single property's fields"""
    
    analysis = {
        'city': city,
        'property_index': index
    }
    
    # Copy all existing fields
    for key, value in prop.items():
        analysis[key] = value
    
    # Analyze property type
    analysis['detected_property_type'] = detect_property_type_from_data(prop)
    
    # Analyze posted by information
    analysis['posted_by_category'] = categorize_posted_by(prop)
    
    # Description analysis
    analysis['has_description'] = bool(prop.get('description', '').strip())
    analysis['description_length'] = len(str(prop.get('description', '')))
    
    # URL analysis
    analysis['has_property_url'] = bool(prop.get('property_url', '').strip())
    analysis['url_type'] = analyze_url_type(prop.get('property_url', ''))
    
    # Premium analysis
    analysis['is_premium_property'] = prop.get('is_premium', False)
    analysis['premium_indicators_count'] = len(prop.get('premium_indicators', []))
    
    # Field completeness score
    total_fields = len([k for k in prop.keys() if not k.startswith('_')])
    filled_fields = len([k for k, v in prop.items() if v and str(v).strip() and not k.startswith('_')])
    analysis['field_completeness_percentage'] = (filled_fields / total_fields * 100) if total_fields > 0 else 0
    
    return analysis

def detect_property_type_from_data(prop):
    """Detect property type from scraped data"""
    
    title = str(prop.get('title', '')).lower()
    prop_type = str(prop.get('property_type', '')).lower()
    
    # Check explicit property type field first
    if prop_type:
        return prop_type
    
    # Detect from title
    if any(keyword in title for keyword in ['apartment', 'flat']):
        return 'apartment'
    elif any(keyword in title for keyword in ['house', 'villa', 'independent']):
        return 'house'
    elif any(keyword in title for keyword in ['builder floor', 'floor']):
        return 'builder_floor'
    elif any(keyword in title for keyword in ['plot', 'land']):
        return 'plot'
    elif any(keyword in title for keyword in ['commercial', 'office', 'shop']):
        return 'commercial'
    else:
        return 'unknown'

def categorize_posted_by(prop):
    """Categorize the 'posted by' information"""
    
    owner_name = str(prop.get('owner_name', '')).lower()
    premium_type = str(prop.get('premium_type', '')).lower()
    premium_indicators = prop.get('premium_indicators', [])
    
    # Check for builder
    if any(keyword in owner_name for keyword in ['builder', 'construction', 'developers']):
        return 'builder'
    
    # Check for dealer/agent
    if any(keyword in owner_name for keyword in ['dealer', 'agent', 'consultant', 'property']):
        return 'dealer'
    
    # Check for premium membership
    if premium_type == 'premium' or any('premium' in str(indicator).lower() for indicator in premium_indicators):
        return 'premium_member'
    
    # Check for owner
    if 'owner:' in owner_name:
        return 'owner'
    
    return 'unknown'

def analyze_url_type(url):
    """Analyze the type of property URL"""
    
    if not url:
        return 'missing'
    
    url_lower = url.lower()
    
    if 'pdpid' in url_lower:
        return 'individual_property'
    elif 'project' in url_lower:
        return 'project_page'
    elif 'builder' in url_lower:
        return 'builder_page'
    else:
        return 'other'

def print_property_analysis(analysis):
    """Print detailed analysis of a property"""
    
    print(f'   📝 Title: {analysis.get("title", "NOT FOUND")[:60]}...')
    print(f'   💰 Price: {analysis.get("price", "NOT FOUND")}')
    print(f'   📏 Area: {analysis.get("area", "NOT FOUND")}')
    print(f'   🏠 Type: {analysis.get("detected_property_type", "NOT FOUND")}')
    print(f'   👤 Posted By: {analysis.get("posted_by_category", "NOT FOUND")} ({analysis.get("owner_name", "")[:30]})')
    print(f'   📸 Photos: {analysis.get("photo_count", "NOT FOUND")}')
    print(f'   📞 Contact: {analysis.get("contact_options", "NOT FOUND")[:40]}...')
    print(f'   📝 Description: {"YES" if analysis.get("has_description") else "NO"} ({analysis.get("description_length", 0)} chars)')
    print(f'   🔗 URL Type: {analysis.get("url_type", "NOT FOUND")}')
    print(f'   ⭐ Premium: {"YES" if analysis.get("is_premium_property") else "NO"}')
    print(f'   📊 Completeness: {analysis.get("field_completeness_percentage", 0):.1f}%')

if __name__ == "__main__":
    deep_field_validation()
